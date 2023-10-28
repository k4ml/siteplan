import os
import sys
import click

import gunicorn.util

from .app import App

@click.group()
@click.pass_context
@click.option('--debug/--no-debug', default=False)
@click.option('--app', default=None)
@click.option('--settings', default="siteplan.settings")
def cli(ctx, debug=False, app=None, settings=None):
    sys.path.insert(0, os.getcwd())
    ctx.ensure_object(dict)

    if os.path.isdir("myapp"):
        settings = "myapp.settings"
    os.environ["DJANGO_SETTINGS_MODULE"] = settings
    if app is not None:
        app = gunicorn.util.import_app(app)
        print("Got custom app,", app)
    else:
        from django.core.wsgi import get_wsgi_application
        app = get_wsgi_application()

    ctx.obj["siteplan_app"] = app
    ctx.obj["siteplan_settings"] = settings
    click.echo(debug)

@cli.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("manage_args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def manage(ctx, manage_args):
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    manage_args = list(manage_args)
    execute_from_command_line(["manage"] + manage_args)


@click.option("--address", "-b", default="127.0.0.1:9000")
@click.option("--no-serve-static", default=False)
@click.option("--reload/--no-reload", "reload_", default=False)
@cli.command()
@click.pass_context
def run(ctx, address, no_serve_static=False, reload_=False):
    from .server import run as server_run

    return server_run(ctx.obj["siteplan_app"], address, not no_serve_static, reload_)


@cli.command()
@click.pass_context
def hello(ctx):
    click.echo(ctx.parent)


@click.option("--copy-dir/--no-copy-dir", default=True)
@click.option("--siteplan-exe", default="./venv/bin/siteplan")
@cli.command()
@click.pass_context
def init_app(ctx, copy_dir=True, siteplan_exe="./venv/bin/siteplan"):
    if copy_dir:
        from shutil import copytree
        from siteplan.settings import SETTINGS_DIR
        copytree(SETTINGS_DIR / "myapp_templates", ".", dirs_exist_ok=True)
        copytree(SETTINGS_DIR / "templates", "myapp/templates", dirs_exist_ok=True)

    from django.core.management import call_command
    from .app import setup
    import subprocess

    os.environ["DJANGO_SETTINGS_MODULE"] = "myapp.settings"
    subprocess.run(["bun", "install"])
    #subprocess.run(["bun", "run", "mix"])
    subprocess.run([siteplan_exe, "manage", "collectstatic", "--no-input"])
    subprocess.run([siteplan_exe, "manage", "migrate"])
    print("Populating data ...")
    setup()

#cli.add_command(manage)
#cli.add_command(run_gunicorn)

def main():
    cli(obj={})

if __name__ == "__main__":
    main()
