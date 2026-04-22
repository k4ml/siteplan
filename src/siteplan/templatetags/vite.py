import os
import json
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def vite(path):
    manifest_path = os.path.join(settings.BASE_DIR, "static", "manifest.json")
    if not os.path.exists(manifest_path):
        return ""

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except (IOError, json.JSONDecodeError):
        return ""

    asset_info = manifest.get(path)

    if not asset_info:
        return ""

    return mark_safe(os.path.join(settings.STATIC_URL, asset_info['file']))
