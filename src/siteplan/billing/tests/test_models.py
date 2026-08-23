import pytest
from django.db import IntegrityError
from django.test import Client


@pytest.mark.django_db
def test_plan_creation():
    from siteplan.billing.models import Plan

    plan = Plan.objects.create(
        name="Pro", description="Pro plan",
        prices=[{"currency": "usd", "amount": "25.00"}],
        features=["10 projects", "Priority support"],
    )
    assert plan.name == "Pro"
    assert plan.is_active is True
    assert len(plan.features) == 2
    assert str(plan) == "Pro"


@pytest.mark.django_db
def test_plan_get_price():
    from siteplan.billing.models import Plan

    plan = Plan.objects.create(
        name="Multi", prices=[
            {"currency": "usd", "amount": "10.00"},
            {"currency": "myr", "amount": "45.00"},
        ],
    )
    assert plan.get_price("usd")["amount"] == "10.00"
    assert plan.get_price("myr")["amount"] == "45.00"
    assert plan.get_price("eur")["amount"] == "10.00"  # fallback to first
    assert plan.get_price()["amount"] == "10.00"  # default currency


@pytest.mark.django_db
def test_plan_supported_currencies(plan):
    assert plan.supported_currencies() == ["usd", "myr"]


@pytest.mark.django_db
def test_gateway_config_singleton():
    from siteplan.billing.models import GatewayConfig

    config = GatewayConfig.load()
    assert config.pk == 1
    assert config.active_gateway == "dummy"

    config2 = GatewayConfig.load()
    assert config2.pk == 1
    assert GatewayConfig.objects.count() == 1


@pytest.mark.django_db
def test_subscription_unique_active_per_user(user, plan):
    from siteplan.billing.models import Subscription

    Subscription.objects.create(
        user=user, plan=plan, status="active", gateway="dummy",
        gateway_subscription_id="sub_1",
    )
    with pytest.raises(IntegrityError):
        Subscription.objects.create(
            user=user, plan=plan, status="active", gateway="dummy",
            gateway_subscription_id="sub_2",
        )


@pytest.mark.django_db
def test_subscription_allows_multiple_inactive(user, plan):
    from siteplan.billing.models import Subscription

    Subscription.objects.create(
        user=user, plan=plan, status="cancelled", gateway="dummy",
        gateway_subscription_id="sub_1",
    )
    Subscription.objects.create(
        user=user, plan=plan, status="cancelled", gateway="dummy",
        gateway_subscription_id="sub_2",
    )
    assert Subscription.objects.filter(user=user).count() == 2
