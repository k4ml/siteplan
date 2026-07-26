from django.shortcuts import redirect
from django.urls import path

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
from django.contrib.auth.mixins import LoginRequiredMixin

app_name = "billing"

plan_crud = PlanCRUD()


class StaffCRUDListView(StaffRequiredMixin, LoginRequiredMixin, CRUDListView):
    pass


class StaffCRUDCreateView(StaffRequiredMixin, LoginRequiredMixin, CRUDCreateView):
    pass


class StaffCRUDUpdateView(StaffRequiredMixin, LoginRequiredMixin, CRUDUpdateView):
    pass


class StaffCRUDDeleteView(StaffRequiredMixin, LoginRequiredMixin, CRUDDeleteView):
    pass


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
