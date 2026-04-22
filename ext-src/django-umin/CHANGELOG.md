# Changelog

All notable changes to django-umin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Proxy and HMR support**: Added support for proxied development environments (e.g., GitHub Codespaces). New settings allow configuring custom dev server URLs and WebSocket connections for Hot Module Replacement (HMR):
  - `DJANGO_UMIN_VITE_DEV_SERVER_URL`: Full base URL for the dev server (e.g., `https://codespace-5173.app.github.dev`)
  - `DJANGO_UMIN_VITE_DEV_SERVER_PROTOCOL`: Protocol for dev server (e.g., `https`, default: `http`)
  - `DJANGO_UMIN_VITE_HMR_PROTOCOL`: Protocol for HMR WebSocket connection (e.g., `wss`)
  - `DJANGO_UMIN_VITE_HMR_HOST`: Host for HMR connection
  - `DJANGO_UMIN_VITE_HMR_PORT`: Port for HMR connection
  - `DJANGO_UMIN_VITE_HMR_CLIENT_PORT`: Client-side port for HMR
- **--keep-vite-config option**: Added `--keep-vite-config` flag to `vite_dev` command to preserve the temporary Vite configuration file after the server stops. Useful for debugging and inspecting the generated configuration. Defaults to `False` (deletes the config file).

### Fixed
- **vite_dev command now watches all apps**: The `vite_dev` management command now watches all Django apps with `fe/` directories simultaneously, instead of being limited to a single app. This ensures that changes to frontend assets in any app (e.g., `labzero/fe/`, `myapp/fe/`) trigger hot module replacement (HMR).
- **vite_asset template tag URLs in dev mode**: Fixed the `vite_asset` template tag to generate correct URLs for the multi-app Vite dev server. URLs now include the full path from project root to the asset file (e.g., `http://localhost:5173/static/ext-src/labzero/src/labzero/fe/css/app.css`).
- **Proxied environment support**: The `vite_asset` template tag now respects `DJANGO_UMIN_VITE_DEV_SERVER_URL` and `DJANGO_UMIN_VITE_DEV_SERVER_PROTOCOL` settings, allowing proper asset URLs in proxied environments.
- **Cloudflare tunnel and proxy host blocking**: Fixed "Blocked request" errors when accessing the dev server through Cloudflare tunnels, ngrok, or other proxy services. Vite server now configured with:
  - `allowedHosts: ['.']` to accept requests from any hostname
  - Permissive CORS (`origin: '*'`) and appropriate headers
  - No Django `ALLOWED_HOSTS` configuration required for Vite dev server

### Changed
- **vite_dev command API**: Changed from positional `app_name` argument to optional `--app` flag that can be specified multiple times. If no apps are specified, all apps with `fe/` directories are watched automatically.
- Auto-discovery of all apps with frontend assets
- Support for watching multiple apps simultaneously
- Improved Vite configuration with proper file system access and watch patterns
- Documentation for Vite development workflow and proxied environments

## [0.1.0] - 2024-02-01

### Added
- Initial release
- Django Admin-style CRUD API
- HTMX integration
- Tailwind CSS templates
- Vite build support
- Template tags for asset management
