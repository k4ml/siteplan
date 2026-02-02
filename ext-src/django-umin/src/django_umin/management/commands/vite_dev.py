import os
import subprocess
import tempfile
import glob
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from django.apps import apps


class Command(BaseCommand):
    help = "Runs a Vite dev server that watches all apps with frontend assets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            type=str,
            action="append",
            dest="app_names",
            help="Specific app(s) to watch. Can be used multiple times. If not specified, watches all apps with 'fe' directories.",
        )

    def handle(self, *args, **options):
        project_root = str(settings.BASE_DIR)

        node_modules_path = os.path.join(project_root, "node_modules")
        if not os.path.isdir(node_modules_path):
            self.stderr.write(
                self.style.ERROR(
                    "node_modules directory not found. Please run 'npm install'."
                )
            )
            return

        # Discover apps with 'fe' directories
        app_configs = self.discover_vite_apps(options.get("app_names"))

        if not app_configs:
            self.stderr.write(
                self.style.ERROR(
                    "No apps with 'fe' directories found. "
                    "Create a 'fe' directory in your app to use Vite."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Starting Vite dev server for {len(app_configs)} app(s): "
                f"{', '.join([ac.name for ac in app_configs])}"
            )
        )

        vite_config_content = self.generate_vite_config(project_root, app_configs)

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

    def discover_vite_apps(self, specified_app_names=None):
        """Discover all apps with 'fe' directories, or specific apps if provided."""
        app_configs = []

        if specified_app_names:
            # Watch only specified apps
            for app_name in specified_app_names:
                try:
                    app_config = apps.get_app_config(app_name)
                    fe_dir = os.path.join(app_config.path, "fe")
                    if os.path.exists(fe_dir):
                        app_configs.append(app_config)
                    else:
                        self.stderr.write(
                            self.style.WARNING(
                                f"App '{app_name}' does not have a 'fe' directory. Skipping."
                            )
                        )
                except LookupError:
                    self.stderr.write(self.style.ERROR(f"App '{app_name}' not found."))
        else:
            # Auto-discover all apps with 'fe' directories
            for app_config in apps.get_app_configs():
                fe_dir = os.path.join(app_config.path, "fe")
                if os.path.exists(fe_dir):
                    app_configs.append(app_config)

        return app_configs

    def discover_assets(self, fe_dir, app_name):
        """Discover CSS and JS assets in the frontend directory."""
        assets = {}

        # Discover CSS files
        css_dir = os.path.join(fe_dir, "css")
        if os.path.exists(css_dir):
            css_files = glob.glob(os.path.join(css_dir, "*.css"))
            for css_file in css_files:
                filename = os.path.basename(css_file)
                name_without_ext = os.path.splitext(filename)[0]
                rel_path = os.path.relpath(css_file, fe_dir)
                assets[f"{app_name}-{name_without_ext}-css"] = rel_path

        # Discover JS files (including subdirectories)
        js_dir = os.path.join(fe_dir, "js")
        if os.path.exists(js_dir):
            js_files = glob.glob(os.path.join(js_dir, "**", "*.js"), recursive=True)
            for js_file in js_files:
                rel_path = os.path.relpath(js_file, fe_dir)
                filename = os.path.basename(js_file)
                name_without_ext = os.path.splitext(filename)[0]
                # Use relative path for asset name to avoid conflicts
                path_without_ext = (
                    os.path.splitext(rel_path)[0].replace("/", "-").replace("\\", "-")
                )
                assets[f"{app_name}-{path_without_ext}-js"] = rel_path

        return assets

    def generate_vite_config(self, project_root, app_configs):
        """Generate a Vite config that watches all specified apps."""

        # Collect all watched directories
        all_watched_dirs = []

        for app_config in app_configs:
            fe_dir = os.path.join(app_config.path, "fe")
            rel_fe_dir = os.path.relpath(fe_dir, project_root).replace("\\", "/")
            all_watched_dirs.append(rel_fe_dir)

        # Format watched directories for the config
        watched_dirs_config = ",\n        ".join(
            [f"resolve('{d}')" for d in all_watched_dirs]
        )

        return f"""
import {{ defineConfig }} from 'vite';
import {{ resolve }} from 'path';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({{
  // Use project root as the base to serve from all app directories
  root: resolve('.'),

  // The base URL for assets
  base: '/static/',

  plugins: [
    tailwindcss(),
  ],

  server: {{
    host: '0.0.0.0',
    port: {getattr(settings, "DJANGO_UMIN_VITE_DEV_SERVER_PORT", 5173)},

    // Configure file system access
    fs: {{
      // Allow serving files from these directories
      allow: [
        resolve('.'),
        {watched_dirs_config}
      ]
    }},

    // Watch configuration to include all app fe directories
    watch: {{
      // Watch these directories for changes
      include: [{", ".join([f"'{d}/**/*'" for d in all_watched_dirs])}],
    }}
  }},
}});
"""
