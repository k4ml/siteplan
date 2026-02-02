# Changelog

All notable changes to django-umin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **vite_dev command now watches all apps**: The `vite_dev` management command now watches all Django apps with `fe/` directories simultaneously, instead of being limited to a single app. This ensures that changes to frontend assets in any app (e.g., `labzero/fe/`, `myapp/fe/`) trigger hot module replacement (HMR).
- **vite_asset template tag URLs in dev mode**: Fixed the `vite_asset` template tag to generate correct URLs for the multi-app Vite dev server. URLs now include the full path from project root to the asset file (e.g., `http://localhost:5173/static/ext-src/labzero/src/labzero/fe/css/app.css`).

### Changed
- **vite_dev command API**: Changed from positional `app_name` argument to optional `--app` flag that can be specified multiple times. If no apps are specified, all apps with `fe/` directories are watched automatically.

### Added
- Auto-discovery of all apps with frontend assets
- Support for watching multiple apps simultaneously
- Improved Vite configuration with proper file system access and watch patterns
- Documentation for Vite development workflow

## [0.1.0] - 2024-02-01

### Added
- Initial release
- Django Admin-style CRUD API
- HTMX integration
- Tailwind CSS templates
- Vite build support
- Template tags for asset management
