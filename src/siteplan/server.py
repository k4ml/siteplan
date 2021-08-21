
import os

def run(app, address="127.0.0.1:9000", serve_static=False, reload_=False):
    import multiprocessing
    from whitenoise import WhiteNoise
    from gunicorn.app.base import BaseApplication
    from django.conf import settings

    class GunicornApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {
                key: value
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            }
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        "bind": address,
        "workers": (multiprocessing.cpu_count() * 2) + 1,
        "accesslog": "-",
        "reload": reload_,
    }

    if serve_static:
        # serve files from directory ./static/ but also
        # serve files from other installed apps collected
        # through `collectstatic` command into STATIC_ROOT dir
        static_dir = os.path.join(os.getcwd(), "static")
        static_root_dir = os.path.join(os.getcwd(), "public")
        app = WhiteNoise(app, root=static_dir)
        app.add_files(static_root_dir, prefix="/static/")
        app.add_files(static_dir, prefix="/static/")

    ret = GunicornApplication(app, options).run()
    return ret
