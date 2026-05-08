from django import template
from django.utils.safestring import mark_safe

from siteplan.models import AnalyticsSetting

register = template.Library()


@register.simple_tag(takes_context=True)
def analytics_code(context, placement):
    """Return the analytics tracking code for the current site if placement
    matches the configured value and the current request path is not excluded.

    Args:
        placement: Either 'head' or 'body'. The tag only renders when the
                   setting's placement field matches this value.
    """
    request = context.get("request")
    if request is None:
        return ""

    try:
        setting = AnalyticsSetting.for_request(request)
    except AnalyticsSetting.DoesNotExist:
        return ""

    if not setting.analytics_code or setting.placement != placement:
        return ""

    current_path = request.path
    excluded = [
        p.strip()
        for p in setting.excluded_paths.splitlines()
        if p.strip()
    ]
    for prefix in excluded:
        if current_path.startswith(prefix):
            return ""

    return mark_safe(setting.analytics_code)