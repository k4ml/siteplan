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

    locale, _ = Locale.objects.get_or_create(language_code="en")
    ct = ContentType.objects.get_for_model(Page)
    root, _ = Page.objects.get_or_create(
        title="Root", slug="root", content_type=ct, locale=locale,
        defaults={"depth": 1, "path": "0001"},
    )
    Site.objects.get_or_create(
        hostname="localhost", port=80,
        defaults={"root_page": root, "is_default_site": True},
    )


@pytest.fixture
def user():
    from django.contrib.auth import get_user_model

    return get_user_model().objects.create_user(
        email="planuser@example.com", password="testpass123!", name="Test User",
    )


@pytest.fixture
def staff_user():
    from django.contrib.auth import get_user_model

    return get_user_model().objects.create_user(
        email="staff@example.com", password="testpass123!",
        name="Staff User", is_staff=True,
    )


@pytest.fixture
def plan():
    from siteplan.billing.models import Plan

    return Plan.objects.create(
        name="Basic",
        description="Basic plan",
        prices=[
            {"currency": "usd", "amount": "10.00", "stripe_price_id": None},
            {"currency": "myr", "amount": "45.00", "stripe_price_id": None},
        ],
        features=["Feature A", "Feature B"],
        is_active=True,
    )


@pytest.fixture
def subscription(user, plan):
    from siteplan.billing.models import Subscription

    return Subscription.objects.create(
        user=user, plan=plan, status="active", gateway="dummy",
        gateway_subscription_id="dummy_sub_1_1",
        amount="10.00", currency="usd",
    )
