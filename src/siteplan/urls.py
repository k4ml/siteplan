from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from siteplan.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    ProfileView,
    dashboard,
    index,
)


urlpatterns = [
    path("", index, name="index"),
    path("app/", dashboard, name="dashboard"),
    path("app/profile/", ProfileView.as_view(), name="profile"),
    path(
        "app/password/change/",
        PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("app/billing/", include("siteplan.billing.urls")),
    path("crud/", lambda r: redirect("billing:crud_index"), name="crud_index"),
    path("admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("pages/", include(wagtail_urls)),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
