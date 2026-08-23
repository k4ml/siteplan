from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import path
from django.utils.translation import gettext_lazy as _

from django_umin.views import CRUDListView, CRUDCreateView, CRUDUpdateView, CRUDDeleteView

from .views import (
    GatewayConfigView,
    PlanCRUD,
    StaffRequiredMixin,
    cancel_subscription,
    stripe_webhook,
    subscribe,
    subscribe_plan,
    subscription_list,
)

app_name = "billing"

plan_crud = PlanCRUD()


class StaffCRUDListView(StaffRequiredMixin, LoginRequiredMixin, CRUDListView):
    pass


class StaffCRUDCreateView(StaffRequiredMixin, LoginRequiredMixin, CRUDCreateView):
    pass


class StaffCRUDUpdateView(StaffRequiredMixin, LoginRequiredMixin, CRUDUpdateView):
    pass


class StaffCRUDDeleteView(StaffRequiredMixin, LoginRequiredMixin, CRUDDeleteView):
    def form_valid(self, form):
        obj = self.get_object()
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                _("Cannot delete {name}: it has active or past subscriptions.").format(
                    name=obj
                ),
            )
            queryset = self.crud_view.get_queryset(self.request)
            context = {
                "object_list": queryset,
                "crud_view": self.crud_view,
                "model_name": self.crud_view.model._meta.verbose_name,
                "model_name_plural": self.crud_view.model._meta.verbose_name_plural,
                "search_query": self.request.GET.get("q", ""),
                "list_display": self.crud_view.list_display,
                "list_display_links": self.crud_view.list_display_links,
                "has_add_permission": True,
                "url_namespace": self.crud_view.get_url_namespace(),
                "messages": list(messages.get_messages(self.request)),
                "is_paginated": False,
            }
            html = render_to_string(
                "django_umin/list_content.html", context, self.request
            )
            response = HttpResponse(html)
            response["HX-Trigger"] = "showMessage"
            return response


def crud_index(request):
    return redirect("billing:plan_list")


urlpatterns = [
    path("plans/", StaffCRUDListView.as_view(crud_view=plan_crud), name="plan_list"),
    path("plans/create/", StaffCRUDCreateView.as_view(crud_view=plan_crud), name="plan_create"),
    path("plans/<int:pk>/", StaffCRUDUpdateView.as_view(crud_view=plan_crud), name="plan_update"),
    path("plans/<int:pk>/delete/", StaffCRUDDeleteView.as_view(crud_view=plan_crud), name="plan_delete"),
    path("", crud_index, name="crud_index"),
    path("gateway/", GatewayConfigView.as_view(), name="gateway_config"),
    path("subscribe/", subscribe_plan, name="subscribe_plan"),
    path("subscribe/<int:plan_id>/", subscribe, name="subscribe"),
    path("subscriptions/", subscription_list, name="subscription_list"),
    path("subscriptions/<int:subscription_id>/cancel/", cancel_subscription, name="cancel_subscription"),
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
]
