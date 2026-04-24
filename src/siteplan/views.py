from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView


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
