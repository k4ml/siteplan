"""Tests for the vite_asset template tag."""

import os
from unittest.mock import Mock, patch

import pytest
from django.apps import AppConfig


def test_vite_asset_dev_mode_css(settings):
    """Test that vite_asset generates correct CSS URLs in dev mode."""
    settings.DJANGO_UMIN_VITE_DEV_MODE = True
    settings.DJANGO_UMIN_VITE_DEV_SERVER_HOST = "localhost"
    settings.DJANGO_UMIN_VITE_DEV_SERVER_PORT = 5173
    settings.BASE_DIR = "/project/root"

    from django_umin.templatetags.django_umin_vite import vite_asset

    # Mock app config
    mock_app = Mock(spec=AppConfig)
    mock_app.path = "/project/root/ext-src/labzero/src/labzero"

    with patch("django_umin.templatetags.django_umin_vite.apps") as mock_apps:
        mock_apps.get_app_config.return_value = mock_app

        result = vite_asset("css/app.css", "labzero")

    expected = '<link rel="stylesheet" href="http://localhost:5173/static/ext-src/labzero/src/labzero/fe/css/app.css">'
    assert result == expected


def test_vite_asset_dev_mode_js(settings):
    """Test that vite_asset generates correct JS URLs in dev mode."""
    settings.DJANGO_UMIN_VITE_DEV_MODE = True
    settings.DJANGO_UMIN_VITE_DEV_SERVER_HOST = "localhost"
    settings.DJANGO_UMIN_VITE_DEV_SERVER_PORT = 5173
    settings.BASE_DIR = "/project/root"

    from django_umin.templatetags.django_umin_vite import vite_asset

    # Mock app config
    mock_app = Mock(spec=AppConfig)
    mock_app.path = "/project/root/src/myapp"

    with patch("django_umin.templatetags.django_umin_vite.apps") as mock_apps:
        mock_apps.get_app_config.return_value = mock_app

        result = vite_asset("js/main.js", "myapp")

    expected = '<script type="module" src="http://localhost:5173/static/src/myapp/fe/js/main.js"></script>'
    assert result == expected


def test_vite_asset_dev_mode_vite_client(settings):
    """Test that @vite/client is served from root."""
    settings.DJANGO_UMIN_VITE_DEV_MODE = True
    settings.DJANGO_UMIN_VITE_DEV_SERVER_HOST = "localhost"
    settings.DJANGO_UMIN_VITE_DEV_SERVER_PORT = 5173

    from django_umin.templatetags.django_umin_vite import vite_asset

    result = vite_asset("@vite/client", "")

    expected = (
        '<script type="module" src="http://localhost:5173/@vite/client"></script>'
    )
    assert result == expected


def test_vite_asset_dev_mode_different_apps(settings):
    """Test that vite_asset works correctly for different apps."""
    settings.DJANGO_UMIN_VITE_DEV_MODE = True
    settings.DJANGO_UMIN_VITE_DEV_SERVER_HOST = "localhost"
    settings.DJANGO_UMIN_VITE_DEV_SERVER_PORT = 5173
    settings.BASE_DIR = "/project/root"

    from django_umin.templatetags.django_umin_vite import vite_asset

    apps = {
        "labzero": Mock(
            spec=AppConfig, path="/project/root/ext-src/labzero/src/labzero"
        ),
        "myapp": Mock(spec=AppConfig, path="/project/root/src/myapp"),
        "django_umin": Mock(
            spec=AppConfig, path="/project/root/ext-src/django-umin/src/django_umin"
        ),
    }

    with patch("django_umin.templatetags.django_umin_vite.apps") as mock_apps:
        mock_apps.get_app_config.side_effect = lambda name: apps[name]

        # Test each app
        result1 = vite_asset("css/app.css", "labzero")
        assert "ext-src/labzero/src/labzero/fe/css/app.css" in result1

        result2 = vite_asset("css/app.css", "myapp")
        assert "src/myapp/fe/css/app.css" in result2

        result3 = vite_asset("css/app.css", "django_umin")
        assert "ext-src/django-umin/src/django_umin/fe/css/app.css" in result3


def test_vite_asset_app_not_found(settings):
    """Test that RuntimeError is raised for non-existent app."""
    settings.DJANGO_UMIN_VITE_DEV_MODE = True

    from django_umin.templatetags.django_umin_vite import vite_asset

    with patch("django_umin.templatetags.django_umin_vite.apps") as mock_apps:
        mock_apps.get_app_config.side_effect = LookupError()

        with pytest.raises(RuntimeError, match="Application 'nonexistent' not found"):
            vite_asset("css/app.css", "nonexistent")
