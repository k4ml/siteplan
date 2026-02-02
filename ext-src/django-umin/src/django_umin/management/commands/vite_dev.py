import os
import subprocess
import tempfile
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from django.apps import apps
class Command(BaseCommand):
    help = "Runs a single Vite dev server for a specific app."

    def add_arguments(self, parser):
        parser.add_argument(
            "app_name",
            type=str,
            help="The name of the app to run the dev server for.",
            default="labzero",
            nargs="?",
        )

    def handle(self, *args, **options):
        project_root = str(settings.BASE_DIR)
        app_name = options["app_name"]

        try:
            app_config = apps.get_app_config(app_name)
        except LookupError:
            self.stderr.write(self.style.ERROR(f"App '{app_name}' not found."))
            return

        node_modules_path = os.path.join(project_root, "node_modules")
        if not os.path.isdir(node_modules_path):
            self.stderr.write(
                self.style.ERROR(
                    "node_modules directory not found. Please run 'npm install'."
                )
            )
            return

        self.stdout.write(f"Starting Vite dev server for app '{app_name}'...")

        vite_config_content = self.generate_vite_config(
            project_root, app_config.path, app_name
        )

        temp_config_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".js", dir=project_root
            ) as f:
                f.write(vite_config_content)
                temp_config_file = f.name

            self.stdout.write(f"Using temporary config: {temp_config_file}")

            command = ["npx", "vite", "--config", temp_config_file]

            # This will run indefinitely until the user stops it with Ctrl+C
            subprocess.run(command, cwd=project_root, check=True)

        except subprocess.CalledProcessError:
            self.stderr.write(self.style.ERROR("Vite dev server stopped unexpectedly."))
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS("Vite dev server stopped successfully.")
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
        finally:
            if temp_config_file and os.path.exists(temp_config_file):
                os.remove(temp_config_file)
                self.stdout.write(
                    f"Cleaned up temporary config file {temp_config_file}"
                )

    def generate_vite_config(self, project_root, app_path, app_name):
        source_dir = os.path.join(app_path, "fe")
        rel_source_dir = os.path.relpath(source_dir, project_root)

        return f"""
import {{ defineConfig }} from 'vite';
import {{ resolve }} from 'path';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({{
  // Set the root to the app's 'fe' directory
  root: resolve('{rel_source_dir}'),

  // The base URL for assets
  base: '/static/',

  plugins: [
    tailwindcss(),
  ],

  server: {{
    host: '0.0.0.0',
    port: {getattr(settings, "DJANGO_UMIN_VITE_DEV_SERVER_PORT", 5173)},
    // We don't need an entry point, as Django will request assets directly
  }},
}});
"""
