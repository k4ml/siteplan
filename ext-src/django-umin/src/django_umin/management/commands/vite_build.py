import os
import subprocess
import tempfile
import glob
from django.apps import apps
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Discovers and builds Vite assets for all registered Django apps."

    def handle(self, *args, **options):
        self.stdout.write("Starting Vite build process...")

        project_root = str(settings.BASE_DIR)
        node_modules_path = os.path.join(project_root, "node_modules")
        if not os.path.isdir(node_modules_path):
            self.stderr.write(
                self.style.ERROR(
                    "node_modules directory not found. Please run 'npm install'."
                )
            )
            return

        installed_apps = [app.name for app in apps.get_app_configs()]


        for app_name in installed_apps:
            try:
                app_config = apps.get_app_config(app_name.split(".")[-1])
            except LookupError:
                self.stderr.write(f"Could not find app config for {app_name}")
                continue

            app_path = app_config.path
            fe_dir = os.path.join(app_path, "fe")

            if not os.path.exists(fe_dir):
                continue

            # Discover assets dynamically
            assets = self.discover_assets(fe_dir)
            if not assets:
                continue

            self.stdout.write(f"Found Vite-enabled app: {app_name}")

            app_name_simple = app_name.split(".")[-1]

            vite_config_content = self.generate_vite_config(
                project_root, app_path, app_name_simple, assets
            )

            temp_config_file = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".js", dir=project_root
                ) as f:
                    f.write(vite_config_content)
                    temp_config_file = f.name

                self.stdout.write(
                    f"Building {app_name} using config {temp_config_file}..."
                )

                command = ["npx", "vite", "build", "--config", temp_config_file]

                result = subprocess.run(
                    command,
                    cwd=project_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                self.stdout.write(result.stdout)
                if result.stderr:
                    self.stderr.write(result.stderr)

            except subprocess.CalledProcessError as e:
                self.stderr.write(
                    self.style.ERROR(f"Failed to build assets for {app_name}.")
                )
                self.stderr.write(e.stdout)
                self.stderr.write(e.stderr)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
            finally:
                if temp_config_file and os.path.exists(temp_config_file):
                    os.remove(temp_config_file)
                    self.stdout.write(
                        f"Cleaned up temporary config file {temp_config_file}"
                    )

        self.stdout.write(self.style.SUCCESS("Vite assets build process completed."))

    def discover_assets(self, fe_dir):
        """Discover CSS and JS assets in the frontend directory."""
        assets = {}

        # Discover CSS files
        css_dir = os.path.join(fe_dir, "css")
        if os.path.exists(css_dir):
            css_files = glob.glob(os.path.join(css_dir, "*.css"))
            for css_file in css_files:
                filename = os.path.basename(css_file)
                name_without_ext = os.path.splitext(filename)[0]
                assets[f"{name_without_ext}-css"] = os.path.join("css", filename)

        # Discover JS files (including subdirectories)
        js_dir = os.path.join(fe_dir, "js")
        if os.path.exists(js_dir):
            js_files = glob.glob(os.path.join(js_dir, "**", "*.js"), recursive=True)
            for js_file in js_files:
                rel_path = os.path.relpath(js_file, js_dir)
                filename = os.path.basename(js_file)
                name_without_ext = os.path.splitext(filename)[0]
                # Use relative path for asset name to avoid conflicts
                path_without_ext = os.path.splitext(rel_path)[0].replace("/", "-")
                assets[f"{path_without_ext}-js"] = os.path.join("js", rel_path)

        return assets

    def generate_vite_config(self, project_root, app_path, app_name, assets):
        source_dir = os.path.join(app_path, "fe")
        out_dir = os.path.join(app_path, "static", app_name, "dist")

        # We need paths to be relative to the project root for vite
        rel_source_dir = os.path.relpath(source_dir, project_root)
        rel_out_dir = os.path.relpath(out_dir, project_root)

        # Generate input entries dynamically
        input_entries = []
        for asset_name, asset_path in assets.items():
            input_entries.append(
                f"        '{asset_name}': join('{rel_source_dir}', '{asset_path}')"
            )

        input_config = ",\n".join(input_entries)

        return f"""
import {{ defineConfig }} from 'vite';
import {{ resolve, join }} from 'path';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({{
  base: '/static/',
  root: resolve('.'),
  plugins: [
    tailwindcss(),
  ],
  build: {{
    manifest: 'manifest.json',
    outDir: resolve('{rel_out_dir}'),
    rollupOptions: {{
      input: {{
{input_config}
      }},
    }},
    emptyOutDir: true,
  }},
}});
"""
