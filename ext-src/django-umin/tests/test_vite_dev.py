"""Tests for the vite_dev management command."""

import os
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch, call

import pytest
from django.apps import AppConfig
from django.core.management import call_command
from django.test import override_settings


@pytest.fixture
def mock_app_config():
    """Create a mock app config with a fe directory."""
    app_config = Mock(spec=AppConfig)
    app_config.name = "testapp"
    app_config.path = "/fake/path/testapp"
    return app_config


@pytest.fixture
def temp_project_root(tmp_path):
    """Create a temporary project structure with multiple apps."""
    # Create project structure
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create node_modules
    (project_root / "node_modules").mkdir()

    # Create multiple apps with fe directories
    for app_name in ["app1", "app2", "app3"]:
        app_dir = project_root / app_name
        fe_dir = app_dir / "fe"
        fe_dir.mkdir(parents=True)

        # Create some CSS files
        css_dir = fe_dir / "css"
        css_dir.mkdir()
        (css_dir / "app.css").write_text("/* CSS content */")

        # Create some JS files
        js_dir = fe_dir / "js"
        js_dir.mkdir()
        (js_dir / "main.js").write_text("// JS content")

        # Create nested JS files
        page_dir = js_dir / "page"
        page_dir.mkdir()
        (page_dir / "page.js").write_text("// Page JS content")

    return project_root


def test_discover_vite_apps_all(temp_project_root):
    """Test that all apps with fe directories are discovered."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()

    # Mock app configs
    mock_apps = []
    for app_name in ["app1", "app2", "app3"]:
        app_config = Mock(spec=AppConfig)
        app_config.name = app_name
        app_config.path = str(temp_project_root / app_name)
        mock_apps.append(app_config)

    with patch("django_umin.management.commands.vite_dev.apps") as mock_apps_module:
        mock_apps_module.get_app_configs.return_value = mock_apps

        result = cmd.discover_vite_apps(None)

    assert len(result) == 3
    assert all(ac.name in ["app1", "app2", "app3"] for ac in result)


def test_discover_vite_apps_specific(temp_project_root):
    """Test that only specified apps are discovered."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()
    cmd.stderr = StringIO()

    # Mock app configs
    app1_config = Mock(spec=AppConfig)
    app1_config.name = "app1"
    app1_config.path = str(temp_project_root / "app1")

    app2_config = Mock(spec=AppConfig)
    app2_config.name = "app2"
    app2_config.path = str(temp_project_root / "app2")

    with patch("django_umin.management.commands.vite_dev.apps") as mock_apps_module:
        mock_apps_module.get_app_config.side_effect = lambda name: {
            "app1": app1_config,
            "app2": app2_config,
        }[name]

        result = cmd.discover_vite_apps(["app1", "app2"])

    assert len(result) == 2
    assert all(ac.name in ["app1", "app2"] for ac in result)


def test_discover_vite_apps_warns_missing_fe(temp_project_root):
    """Test that warning is issued for apps without fe directory."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()
    cmd.stderr = StringIO()

    # Create an app without fe directory
    app_without_fe = temp_project_root / "app_no_fe"
    app_without_fe.mkdir()

    app_config = Mock(spec=AppConfig)
    app_config.name = "app_no_fe"
    app_config.path = str(app_without_fe)

    with patch("django_umin.management.commands.vite_dev.apps") as mock_apps_module:
        mock_apps_module.get_app_config.return_value = app_config

        result = cmd.discover_vite_apps(["app_no_fe"])

    assert len(result) == 0
    assert "does not have a 'fe' directory" in cmd.stderr.getvalue()


def test_discover_vite_apps_errors_on_nonexistent_app():
    """Test that error is issued for non-existent apps."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()
    cmd.stderr = StringIO()

    with patch("django_umin.management.commands.vite_dev.apps") as mock_apps_module:
        mock_apps_module.get_app_config.side_effect = LookupError("App not found")

        result = cmd.discover_vite_apps(["nonexistent"])

    assert len(result) == 0
    assert "not found" in cmd.stderr.getvalue()


def test_discover_assets(temp_project_root):
    """Test that assets are correctly discovered."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()
    fe_dir = temp_project_root / "app1" / "fe"

    assets = cmd.discover_assets(str(fe_dir), "app1")

    # Check that CSS file is discovered
    assert "app1-app-css" in assets
    assert assets["app1-app-css"] == "css/app.css"

    # Check that JS files are discovered
    assert "app1-js-main-js" in assets
    assert assets["app1-js-main-js"] == "js/main.js"

    assert "app1-js-page-page-js" in assets
    assert assets["app1-js-page-page-js"] == "js/page/page.js"


def test_generate_vite_config_multiple_apps(temp_project_root):
    """Test that vite config correctly includes multiple apps."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()

    # Create mock app configs
    app_configs = []
    for app_name in ["app1", "app2"]:
        app_config = Mock(spec=AppConfig)
        app_config.name = app_name
        app_config.path = str(temp_project_root / app_name)
        app_configs.append(app_config)

    config = cmd.generate_vite_config(str(temp_project_root), app_configs)

    # Verify that both apps are included in the config
    assert "app1" in config
    assert "app2" in config

    # Verify that fs.allow includes both app directories
    assert "app1/fe" in config or "app1\\fe" in config.replace("/", "\\")
    assert "app2/fe" in config or "app2\\fe" in config.replace("/", "\\")

    # Verify basic Vite config structure
    assert "defineConfig" in config
    assert "tailwindcss" in config
    assert "server:" in config
    assert "host: '0.0.0.0'" in config


def test_vite_config_includes_watch_configuration(temp_project_root):
    """Test that vite config includes watch configuration for all apps."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()

    app_configs = []
    for app_name in ["app1", "app2", "app3"]:
        app_config = Mock(spec=AppConfig)
        app_config.name = app_name
        app_config.path = str(temp_project_root / app_name)
        app_configs.append(app_config)

    config = cmd.generate_vite_config(str(temp_project_root), app_configs)

    # Verify watch configuration
    assert "watch:" in config
    assert "include:" in config


@override_settings(
    BASE_DIR="/fake/project",
    DJANGO_UMIN_VITE_DEV_SERVER_PORT=5173,
)
def test_handle_no_node_modules(capsys):
    """Test that command errors when node_modules is missing."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()
    cmd.stdout = StringIO()
    cmd.stderr = StringIO()

    with patch("os.path.isdir", return_value=False):
        cmd.handle()

    assert "node_modules directory not found" in cmd.stderr.getvalue()


@override_settings(
    BASE_DIR="/fake/project",
)
def test_handle_no_apps_with_fe(capsys):
    """Test that command errors when no apps with fe directories exist."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()
    cmd.stdout = StringIO()
    cmd.stderr = StringIO()

    with patch("os.path.isdir", return_value=True):
        with patch("django_umin.management.commands.vite_dev.apps") as mock_apps_module:
            mock_apps_module.get_app_configs.return_value = []

            cmd.handle(app_names=None)

    assert "No apps with 'fe' directories found" in cmd.stderr.getvalue()


@override_settings(
    BASE_DIR="/fake/project",
    DJANGO_UMIN_VITE_DEV_SERVER_PORT=5173,
)
def test_handle_runs_vite_dev_server(temp_project_root):
    """Test that vite dev server is started with correct configuration."""
    from django_umin.management.commands.vite_dev import Command

    cmd = Command()
    cmd.stdout = StringIO()
    cmd.stderr = StringIO()

    # Mock app configs
    app_config = Mock(spec=AppConfig)
    app_config.name = "app1"
    app_config.path = str(temp_project_root / "app1")

    with patch("os.path.isdir", return_value=True):
        with patch("django_umin.management.commands.vite_dev.apps") as mock_apps_module:
            mock_apps_module.get_app_configs.return_value = [app_config]

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = KeyboardInterrupt()

                with patch("tempfile.NamedTemporaryFile") as mock_tempfile:
                    mock_file = Mock()
                    mock_file.name = "/tmp/vite_config_test.js"
                    mock_file.__enter__ = Mock(return_value=mock_file)
                    mock_file.__exit__ = Mock(return_value=False)
                    mock_tempfile.return_value = mock_file

                    with patch("os.path.exists", return_value=True):
                        with patch("os.remove"):
                            cmd.handle(app_names=None)

                # Verify subprocess.run was called with correct arguments
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args[0][0] == [
                    "npx",
                    "vite",
                    "--config",
                    "/tmp/vite_config_test.js",
                ]

    assert "Starting Vite dev server" in cmd.stdout.getvalue()
    assert "stopped successfully" in cmd.stdout.getvalue()
