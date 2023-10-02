
from siteplan.urls import path
from siteplan.urls import urlpatterns as _urlpatterns

from .views import hello

urlpatterns = [
    path("hello/", hello),
] + _urlpatterns
