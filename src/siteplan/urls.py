from django.conf import settings
from django.urls import include, path

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from labzero import views as labzero_views

# Import labzero URL patterns
from labzero.urls import get_urlpatterns
labzero_urlpatterns = get_urlpatterns()

urlpatterns = [
    path("", labzero_views.index),
    path('app/', include((labzero_urlpatterns, 'labzero'))),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('pages/', include(wagtail_urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
