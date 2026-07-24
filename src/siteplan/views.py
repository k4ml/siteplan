from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from siteplan.forms import ProfileForm


def index(request):
    context = {"intro": "Hello world"}
    return render(request, "siteplan/index.html", context)


@login_required
def dashboard(request):
    return render(request, "siteplan/dashboard.html")


class LoginView(DjangoLoginView):
    template_name = "siteplan/login.html"


class LogoutView(DjangoLogoutView):
    template_name = "siteplan/logout.html"


class UminFormMixin:
    """Context contract for django_umin's form_page/form_card templates.

    A view mixing this in renders a fully styled form -- fields, errors, help
    text and submit/cancel buttons -- with no template code of its own; only a
    few class attributes are declared. All rendering is delegated to django_umin.
    """

    form_title = ""
    submit_label = "Save"
    cancel_url = None
    page_title = "Profile"
    htmx_enabled = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "form_title": self.form_title,
                "submit_label": self.submit_label,
                "cancel_url": self.cancel_url,
                "page_title": self.page_title,
                "htmx_enabled": self.htmx_enabled,
            }
        )
        return context


class ProfileView(UminFormMixin, LoginRequiredMixin, UpdateView):
    """Let the signed-in user edit their own name and email."""

    form_class = ProfileForm
    template_name = "siteplan/umin_form.html"
    success_url = reverse_lazy("profile")
    form_title = "Update Profile"
    submit_label = "Save Changes"
    cancel_url = reverse_lazy("dashboard")
    page_title = "Profile"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_change_url"] = reverse("password_change")
        return context

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


class PasswordChangeView(UminFormMixin, DjangoPasswordChangeView):
    """Change the signed-in user's password, rendered by django_umin."""

    template_name = "siteplan/umin_form.html"
    success_url = reverse_lazy("profile")
    form_title = "Change Password"
    submit_label = "Change Password"
    cancel_url = reverse_lazy("profile")
    page_title = "Change Password"

    def form_valid(self, form):
        messages.success(self.request, "Password changed successfully.")
        return super().form_valid(form)
