# Minimal settings stub that imports from labzero.settings
# This file should only contain project-specific overrides

import os
from pathlib import Path

from siteplan import dj_database_url
from labzero.settings import get_base_settings

# Calculate BASE_DIR (3 levels up from this file)
root = Path(__file__).resolve().parent.parent.parent
BASE_DIR = root

# Get base settings from labzero with our BASE_DIR
base_settings = get_base_settings(BASE_DIR=BASE_DIR)

# Apply base settings to current namespace
for key, value in base_settings.items():
    globals()[key] = value

# Project-specific overrides

# Use custom database configuration (override labzero's env.db() approach)
DATABASES = {'default': dj_database_url.config(conn_max_age=600)}
DATABASES["default"]["TEST"] = {
    "NAME": "siteplan_test",
    "USER": "siteplan_test",
}

# Use project-specific user model
AUTH_USER_MODEL = "siteplan_user.User"

# Project-specific WSGI application
WSGI_APPLICATION = "siteplan.wsgi.application"

# Project-specific URL configuration
ROOT_URLCONF = "siteplan.urls"

# Project-specific Wagtail site name
WAGTAIL_SITE_NAME = "My App"

# Update login/redirect URLs to use /app/ paths
LOGIN_REDIRECT_URL = "/app/"
LOGOUT_REDIRECT_URL = "/"

# Use labzero login template
LOGIN_TEMPLATE = "labzero/login.html"

# Use namespaced URLs for login/logout (since they're in labzero namespace)
LOGIN_URL = "/app/login/"

# Add siteplan_user and siteplan to INSTALLED_APPS (keep labzero for core functionality)
INSTALLED_APPS = ["siteplan_user", "siteplan"] + INSTALLED_APPS
