"""Pytest configuration and fixtures."""

import os
import sys
import django
from pathlib import Path
from django.conf import settings as django_settings
import pytest


# Configure Django settings before any tests run
def pytest_configure():
    """Configure Django settings for testing."""
    if not django_settings.configured:
        django_settings.configure(
            DEBUG=True,
            SECRET_KEY="test-secret-key",
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            BASE_DIR=Path("/tmp/test_project"),
            STATIC_URL="/static/",
            STATIC_ROOT="/tmp/test_project/staticfiles",
            # Default Vite settings (matching vite_dev.py defaults)
            DJANGO_UMIN_VITE_DEV_MODE=False,
            DJANGO_UMIN_VITE_DEV_SERVER_HOST="0.0.0.0",
            DJANGO_UMIN_VITE_DEV_SERVER_PORT=5173,
            DJANGO_UMIN_VITE_DEV_SERVER_PROTOCOL="http",
            DJANGO_UMIN_VITE_DEV_SERVER_URL=None,
        )
        django.setup()


@pytest.fixture
def settings():
    """
    Provide Django settings object that can be modified during tests.

    This fixture returns the actual Django settings object, allowing tests
    to override specific settings as needed.
    """
    return django_settings
