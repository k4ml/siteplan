
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
    def __call__(self, environ, start_response):
        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        return application(environ, start_response)


def run():
    execute_from_command_line()
