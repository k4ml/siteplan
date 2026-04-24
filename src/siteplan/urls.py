from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from siteplan.views import index, dashboard, LoginView, LogoutView


urlpatterns = [
    path("", index, name="index"),
    path("app/", dashboard, name="dashboard"),
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
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
