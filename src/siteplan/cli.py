import os
import sys
import click

import gunicorn.util

from .app import App

@click.group()
@click.pass_context
@click.option('--debug/--no-debug', default=False)
@click.option('--app', default=None)
def cli(ctx, debug=False, app=None):
    sys.path.insert(0, os.getcwd())
    ctx.ensure_object(dict)
    if app is not None:
        app = gunicorn.util.import_app(app)
        print("Got custom app,", app)
    else:
        app = App({})

    ctx.obj["siteplan_app"] = app
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
    execute_from_command_line(["manage"] + list(manage_args))


@click.option("--address", "-b", default="127.0.0.1:9000")
@click.option("--serve-static/--no-serve-static", default=False)
@click.option("--reload/--no-reload", "reload_", default=False)
@cli.command()
@click.pass_context
def run(ctx, address, serve_static=False, reload_=False):
    from .server import run as server_run
    return server_run(ctx.obj["siteplan_app"], address, serve_static, reload_)


@cli.command()
@click.pass_context
def hello(ctx):
    click.echo(ctx.parent)

#cli.add_command(manage)
#cli.add_command(run_gunicorn)

def main():
    cli(obj={})

if __name__ == "__main__":
    main()
