from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting
from wagtail.contrib.settings.registry import register_setting


@register_setting
class AnalyticsSetting(BaseSiteSetting):
    analytics_code = models.TextField(
        blank=True,
        help_text=(
            "Paste your analytics tracking code here (e.g. Google Analytics, "
            "Matomo, Plausible, etc.). This code will be injected into every "
            "page that is not listed in the excluded paths."
        ),
    )
    placement = models.CharField(
        max_length=10,
        choices=[
            ("head", "Head (before </head>)"),
            ("body", "Body (before </body>)"),
        ],
        default="head",
        help_text="Where to insert the analytics code in the HTML.",
    )
    excluded_paths = models.TextField(
        blank=True,
        help_text=(
            "URL paths to exclude from analytics, one per line. "
            "Paths are matched by prefix — e.g. '/admin' also matches "
            "'/admin/settings/'. Example: '/admin', '/cms'."
        ),
    )

    panels = [
        FieldPanel("analytics_code"),
        FieldPanel("placement"),
        FieldPanel("excluded_paths"),
    ]