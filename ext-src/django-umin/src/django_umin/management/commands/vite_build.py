import os
import subprocess
import tempfile
from django.apps import apps
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = "Discovers and builds Vite assets for all registered Django apps."

    def handle(self, *args, **options):
        self.stdout.write("Starting Vite build process...")

        installed_apps = [app.name for app in apps.get_app_configs()]
        project_root = str(settings.BASE_DIR)

        for app_name in installed_apps:
            try:
                app_config = apps.get_app_config(app_name.split('.')[-1])
            except LookupError:
                self.stderr.write(f"Could not find app config for {app_name}")
                continue

            app_path = app_config.path
            vite_entry_point = os.path.join(app_path, 'fe', 'js', 'main.js')

            if not os.path.exists(vite_entry_point):
                continue

            self.stdout.write(f"Found Vite-enabled app: {app_name}")

            app_name_simple = app_name.split('.')[-1]

            vite_config_content = self.generate_vite_config(project_root, app_path, app_name_simple)

            temp_config_file = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.js', dir=project_root) as f:
                    f.write(vite_config_content)
                    temp_config_file = f.name

                self.stdout.write(f"Building {app_name} using config {temp_config_file}...")

                command = ['npx', 'vite', 'build', '--config', temp_config_file]

                result = subprocess.run(
                    command,
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    check=True
                )

                self.stdout.write(result.stdout)
                if result.stderr:
                    self.stderr.write(result.stderr)

            except subprocess.CalledProcessError as e:
                self.stderr.write(self.style.ERROR(f"Failed to build assets for {app_name}."))
                self.stderr.write(e.stdout)
                self.stderr.write(e.stderr)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
            finally:
                if temp_config_file and os.path.exists(temp_config_file):
                    os.remove(temp_config_file)
                    self.stdout.write(f"Cleaned up temporary config file {temp_config_file}")

        self.stdout.write(self.style.SUCCESS("Vite assets build process completed."))

    def generate_vite_config(self, project_root, app_path, app_name):
        source_dir = os.path.join(app_path, 'fe')
        out_dir = os.path.join(app_path, 'static', app_name, 'dist')

        # We need paths to be relative to the project root for vite
        rel_source_dir = os.path.relpath(source_dir, project_root)
        rel_out_dir = os.path.relpath(out_dir, project_root)

        return f"""
import {{ defineConfig }} from 'vite';
import {{ resolve, join }} from 'path';

export default defineConfig({{
  base: '/static/',
  root: resolve('{rel_source_dir}'),
  build: {{
    manifest: 'manifest.json',
    outDir: resolve('{rel_out_dir}'),
    rollupOptions: {{
      input: {{
        'app-css': join('{rel_source_dir}', 'css', 'app.css'),
        'main-js': join('{rel_source_dir}', 'js', 'main.js'),
      }},
    }},
    emptyOutDir: true,
  }},
}});
"""
