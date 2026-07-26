
import pytest
from pytest_djangoapp import configure_djangoapp_plugin


def hook(settings):
    return settings


pytest_plugins = configure_djangoapp_plugin(
    settings="siteplan.settings",
    migrate=False,
)

@pytest.fixture(autouse=True)
def _wagtail_site():
    from django.contrib.contenttypes.models import ContentType
    from wagtail.models import Locale, Page, Site
    locale = Locale.objects.create(language_code="en")
    ct = ContentType.objects.get_for_model(Page)
    root = Page.objects.create(
        title="Root", slug="root", content_type=ct, locale=locale, depth=1, path="0001"
    )
    Site.objects.create(
        hostname="localhost", port=80, root_page=root, is_default_site=True
    )


@pytest.fixture
def user(user_model):
    user = user_model(email="user@xxx.com")
    user.save()
    return user
