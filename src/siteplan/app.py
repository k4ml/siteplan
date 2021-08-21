
import os

from django.conf import settings
from django.core.management import execute_from_command_line

def update_settings_from_module(settings, module):
    """Updates a given settings dict from a module denoted by a dotted path.
    :param dict settings:
    :param str module:
    """
    from importlib import import_module

    settings_module = import_module(module)

    settings_dict = {
        key: value
        for key, value in settings_module.__dict__.items()
        if key.upper() == key and not key.startswith('_')
    }
    settings.update(settings_dict)

    return settings

class App(object):
    def __init__(self, conf, urls=None):
        self.urls = urls
        base_conf = update_settings_from_module({}, "siteplan.settings")

        default_conf = {
            "ALLOWED_HOSTS": [
            
            ],
            "DEBUG": True,
            "ROOT_URLCONF": "siteplan.urls",
            "STATIC_ROOT": os.path.join(os.getcwd(), "public"),
            "STATICFILES_DIRS": [
                os.path.join(os.getcwd(), "static"),
            ],
            "STATIC_URL": "/static/",
            "TEMPLATES": [
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [
                        os.path.join(os.getcwd(), "templates"),
                    ],
                    "APP_DIRS": True,
                }
            ],
        }

        default_conf.update(conf)
        base_conf.update(default_conf)

        if not settings.configured:
            settings.configure(**base_conf)



    def __call__(self, environ, start_response):
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        import siteplan.urls
        from django.urls import path
        from django.contrib import admin
        base_patterns = [
            path('admin/', admin.site.urls),
        ]

        if self.urls is not None:
            urlpatterns = self.urls + base_patterns
        else:
            urlpatterns = base_patterns
        siteplan.urls.urlpatterns = urlpatterns
        return application(environ, start_response)


def run():
    execute_from_command_line()
