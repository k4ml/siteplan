from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index


class HomePage(Page):

    # Database fields

    body = RichTextField()

    # Search index configuration

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]


    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
    ]
