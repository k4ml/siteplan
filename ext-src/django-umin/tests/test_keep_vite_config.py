"""Tests for the --keep-vite-config option."""

import os
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from django.apps import AppConfig


def test_vite_config_deleted_by_default(tmp_path, settings):
    """Test that vite config is deleted by default when command stops."""
    from django_umin.management.commands.vite_dev import Command

    settings.BASE_DIR = str(tmp_path)

    cmd = Command()
    cmd.stdout = StringIO()
    cmd.stderr = StringIO()

    # Create node_modules
    (tmp_path / "node_modules").mkdir()

    # Mock app config
    mock_app = Mock(spec=AppConfig)
    mock_app.name = "testapp"
    mock_app.path = str(tmp_path / "testapp")

    # Create fe directory
    fe_dir = tmp_path / "testapp" / "fe"
    fe_dir.mkdir(parents=True)
    (fe_dir / "css").mkdir()
    (fe_dir / "css" / "app.css").write_text("/* test */")

    temp_config_path = None

    with patch("django_umin.management.commands.vite_dev.apps") as mock_apps:
        mock_apps.get_app_configs.return_value = [mock_app]

        with patch("subprocess.run") as mock_run:
            # Simulate KeyboardInterrupt
            mock_run.side_effect = KeyboardInterrupt()

            # Capture the temp config file path
            original_tempfile = tempfile.NamedTemporaryFile

            def capture_tempfile(*args, **kwargs):
                nonlocal temp_config_path
                f = original_tempfile(*args, **kwargs)
                temp_config_path = f.name
                return f

            with patch("tempfile.NamedTemporaryFile", side_effect=capture_tempfile):
                cmd.handle(app_names=None, keep_vite_config=False)

    # Verify config was deleted
    assert temp_config_path is not None
    assert not os.path.exists(temp_config_path)
    assert "Cleaned up temporary config file" in cmd.stdout.getvalue()


def test_vite_config_kept_with_flag(tmp_path, settings):
    """Test that vite config is preserved when --keep-vite-config is used."""
    from django_umin.management.commands.vite_dev import Command

    settings.BASE_DIR = str(tmp_path)

    cmd = Command()
    cmd.stdout = StringIO()
    cmd.stderr = StringIO()

    # Create node_modules
    (tmp_path / "node_modules").mkdir()

    # Mock app config
    mock_app = Mock(spec=AppConfig)
    mock_app.name = "testapp"
    mock_app.path = str(tmp_path / "testapp")

    # Create fe directory
    fe_dir = tmp_path / "testapp" / "fe"
    fe_dir.mkdir(parents=True)
    (fe_dir / "css").mkdir()
    (fe_dir / "css" / "app.css").write_text("/* test */")

    temp_config_path = None

    with patch("django_umin.management.commands.vite_dev.apps") as mock_apps:
        mock_apps.get_app_configs.return_value = [mock_app]

        with patch("subprocess.run") as mock_run:
            # Simulate KeyboardInterrupt
            mock_run.side_effect = KeyboardInterrupt()

            # Capture the temp config file path
            original_tempfile = tempfile.NamedTemporaryFile

            def capture_tempfile(*args, **kwargs):
                nonlocal temp_config_path
                f = original_tempfile(*args, **kwargs)
                temp_config_path = f.name
                return f

            with patch("tempfile.NamedTemporaryFile", side_effect=capture_tempfile):
                cmd.handle(app_names=None, keep_vite_config=True)

    # Verify config still exists
    assert temp_config_path is not None
    assert os.path.exists(temp_config_path)
    assert "Vite config preserved at:" in cmd.stdout.getvalue()

    # Clean up
    os.remove(temp_config_path)


def test_vite_config_content_valid(tmp_path, settings):
    """Test that the preserved config file contains valid Vite configuration."""
    from django_umin.management.commands.vite_dev import Command

    settings.BASE_DIR = str(tmp_path)
    settings.DJANGO_UMIN_VITE_DEV_SERVER_PORT = 5173

    cmd = Command()
    cmd.stdout = StringIO()
    cmd.stderr = StringIO()

    # Create node_modules
    (tmp_path / "node_modules").mkdir()

    # Mock app configs
    apps_data = [
        ("testapp1", tmp_path / "testapp1"),
        ("testapp2", tmp_path / "testapp2"),
    ]

    mock_app_configs = []
    for app_name, app_path in apps_data:
        mock_app = Mock(spec=AppConfig)
        mock_app.name = app_name
        mock_app.path = str(app_path)
        mock_app_configs.append(mock_app)

        # Create fe directory
        fe_dir = app_path / "fe"
        fe_dir.mkdir(parents=True)
        (fe_dir / "css").mkdir()
        (fe_dir / "css" / "app.css").write_text("/* test */")

    temp_config_path = None

    with patch("django_umin.management.commands.vite_dev.apps") as mock_apps:
        mock_apps.get_app_configs.return_value = mock_app_configs

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()

            original_tempfile = tempfile.NamedTemporaryFile

            def capture_tempfile(*args, **kwargs):
                nonlocal temp_config_path
                f = original_tempfile(*args, **kwargs)
                temp_config_path = f.name
                return f

            with patch("tempfile.NamedTemporaryFile", side_effect=capture_tempfile):
                cmd.handle(app_names=None, keep_vite_config=True)

    # Verify config exists and has expected content
    assert temp_config_path is not None
    assert os.path.exists(temp_config_path)

    with open(temp_config_path, "r") as f:
        config_content = f.read()

    # Verify key elements
    assert "defineConfig" in config_content
    assert "tailwindcss" in config_content
    assert "testapp1/fe" in config_content
    assert "testapp2/fe" in config_content
    assert "port: 5173" in config_content
    assert "base: '/static/'" in config_content

    # Clean up
    os.remove(temp_config_path)


def test_vite_config_path_shown_in_output(tmp_path, settings):
    """Test that the temp config path is shown in command output."""
    from django_umin.management.commands.vite_dev import Command

    settings.BASE_DIR = str(tmp_path)

    cmd = Command()
    cmd.stdout = StringIO()
    cmd.stderr = StringIO()

    # Create node_modules
    (tmp_path / "node_modules").mkdir()

    # Mock app config
    mock_app = Mock(spec=AppConfig)
    mock_app.name = "testapp"
    mock_app.path = str(tmp_path / "testapp")

    # Create fe directory
    fe_dir = tmp_path / "testapp" / "fe"
    fe_dir.mkdir(parents=True)
    (fe_dir / "css").mkdir()
    (fe_dir / "css" / "app.css").write_text("/* test */")

    with patch("django_umin.management.commands.vite_dev.apps") as mock_apps:
        mock_apps.get_app_configs.return_value = [mock_app]

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()

            cmd.handle(app_names=None, keep_vite_config=True)

    output = cmd.stdout.getvalue()

    # Verify output messages
    assert "Using temporary config:" in output
    assert "Vite config preserved at:" in output
    assert ".js" in output  # Should show the .js file path
