from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from django_umin.views import CRUDView

from siteplan.views import UminFormMixin

from .forms import GatewayConfigForm
from .gateway import get_gateway
from .gateway.stripe import StripeGateway
from .models import GatewayConfig, Plan, Subscription


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class PlanCRUD(CRUDView):
    model = Plan
    fields = ["name", "description", "price", "features", "is_active", "stripe_price_id"]
    list_display = ["name", "price", "is_active", "created_at"]
    search_fields = ["name", "description"]
    ordering = ["price"]
    list_template = "billing/plan_list.html"
    form_template = "billing/plan_form.html"
    delete_template = "billing/plan_delete.html"
    success_message_create = _("{object} was created successfully.")
    success_message_update = _("{object} was updated successfully.")
    success_message_delete = _("{object} was deleted successfully.")

    def get_form_title(self, action, obj=None):
        return _("{} Plan").format(_(action))

    def get_url_namespace(self):
        return "billing:plan"


class GatewayConfigView(
    StaffRequiredMixin, UminFormMixin, LoginRequiredMixin, UpdateView
):
    model = GatewayConfig
    form_class = GatewayConfigForm
    template_name = "siteplan/umin_form.html"
    success_url = reverse_lazy("billing:gateway_config")
    form_title = _("Payment Gateway Configuration")
    submit_label = _("Save Configuration")
    cancel_url = reverse_lazy("dashboard")
    page_title = _("Gateway Configuration")

    def get_object(self, queryset=None):
        return GatewayConfig.load()

    def form_valid(self, form):
        messages.success(self.request, _("Gateway configuration saved."))
        return super().form_valid(form)


@login_required
def subscribe_plan(request):
    plans = Plan.objects.filter(is_active=True)
    has_active = Subscription.objects.filter(
        user=request.user, status=Subscription.Status.ACTIVE
    ).exists()
    return render(request, "billing/subscribe.html", {
        "plans": plans, "has_active_subscription": has_active,
    })


@login_required
def subscribe(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id, is_active=True)

    if Subscription.objects.filter(user=request.user, status=Subscription.Status.ACTIVE).exists():
        messages.error(request, _("You already have an active subscription."))
        return redirect("billing:subscription_list")

    gateway = get_gateway()

    if isinstance(gateway, StripeGateway):
        session = gateway.create_checkout_session(
            user=request.user, plan=plan,
            success_url=request.build_absolute_uri(
                reverse("billing:subscription_list")
            ),
            cancel_url=request.build_absolute_uri(
                reverse("billing:subscribe_plan")
            ),
        )
        if session:
            return redirect(session["url"])  # pragma: no cover

    result = gateway.create_subscription(request.user, plan)
    Subscription.objects.create(
        user=request.user, plan=plan, status=Subscription.Status.ACTIVE,
        gateway="dummy",
        gateway_subscription_id=result["gateway_subscription_id"],
    )
    messages.success(request, _("Subscription activated!"))
    return redirect("billing:subscription_list")


@login_required
def subscription_list(request):
    subscriptions = (
        Subscription.objects.filter(user=request.user)
        .select_related("plan")
    )
    return render(
        request, "billing/subscription_list.html",
        {"subscriptions": subscriptions},
    )


@login_required
def cancel_subscription(request, subscription_id):
    subscription = get_object_or_404(
        Subscription, pk=subscription_id, user=request.user,
    )
    gateway = get_gateway()
    gateway.cancel_subscription(subscription)
    subscription.status = Subscription.Status.CANCELLED
    subscription.end_date = timezone.now()
    subscription.save()
    messages.success(request, _("Subscription cancelled."))
    return redirect("billing:subscription_list")


@csrf_exempt
def stripe_webhook(request):
    config = GatewayConfig.load()
    gateway = StripeGateway(config)
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    event = gateway.handle_webhook(payload, sig_header)
    return HttpResponse(status=200)
