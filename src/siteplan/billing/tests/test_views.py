import pytest
from django.test import Client

from siteplan.billing.models import GatewayConfig, Plan, Subscription


@pytest.mark.django_db
class TestPlanCRUD:
    def test_plan_list_requires_staff(self, user, staff_user):
        client = Client()
        client.force_login(user)
        response = client.get("/app/billing/plans/")
        assert response.status_code == 403

        client.force_login(staff_user)
        response = client.get("/app/billing/plans/")
        assert response.status_code == 200

    def test_plan_create(self, staff_user):
        client = Client()
        client.force_login(staff_user)
        response = client.post("/app/billing/plans/create/", {
            "name": "Premium",
            "description": "Premium tier",
            "price": "49.00",
            "features": '["Unlimited projects", "24/7 support"]',
            "is_active": True,
        })
        assert response.status_code == 302
        plan = Plan.objects.get(name="Premium")
        assert plan.price == 49.00


@pytest.mark.django_db
class TestGatewayConfigView:
    def test_gateway_config_renders(self, staff_user):
        client = Client()
        client.force_login(staff_user)
        response = client.get("/app/billing/gateway/")
        assert response.status_code == 200
        assert "Gateway Configuration" in response.content.decode()

    def test_gateway_config_requires_staff(self, user):
        client = Client()
        client.force_login(user)
        response = client.get("/app/billing/gateway/")
        assert response.status_code == 403

    def test_gateway_config_update(self, staff_user):
        client = Client()
        client.force_login(staff_user)
        response = client.post("/app/billing/gateway/", {
            "active_gateway": "stripe",
            "stripe_secret_key": "sk_test_123",
        })
        assert response.status_code == 302
        config = GatewayConfig.load()
        assert config.active_gateway == "stripe"
        assert config.stripe_secret_key == "sk_test_123"


@pytest.mark.django_db
class TestSubscribeFlow:
    def test_subscribe_plan_renders(self, user, plan):
        client = Client()
        client.force_login(user)
        response = client.get("/app/billing/subscribe/")
        assert response.status_code == 200
        assert plan.name in response.content.decode()

    def test_subscribe_plan_requires_login(self):
        client = Client()
        response = client.get("/app/billing/subscribe/")
        assert response.status_code == 302

    def test_subscribe_creates_dummy_subscription(self, user, plan):
        client = Client()
        client.force_login(user)
        response = client.post("/app/billing/subscribe/{}/".format(plan.pk))
        assert response.status_code == 302
        sub = Subscription.objects.get(user=user, plan=plan)
        assert sub.status == "active"
        assert sub.gateway == "dummy"

    def test_subscribe_requires_active_plan(self, user, plan):
        plan.is_active = False
        plan.save()
        client = Client()
        client.force_login(user)
        response = client.post("/app/billing/subscribe/{}/".format(plan.pk))
        assert response.status_code == 404


@pytest.mark.django_db
class TestSubscriptionManagement:
    def test_subscription_list(self, user, subscription):
        client = Client()
        client.force_login(user)
        response = client.get("/app/billing/subscriptions/")
        assert response.status_code == 200
        assert subscription.plan.name in response.content.decode()

    def test_subscription_list_requires_login(self):
        client = Client()
        response = client.get("/app/billing/subscriptions/")
        assert response.status_code == 302

    def test_cancel_subscription(self, user, subscription):
        client = Client()
        client.force_login(user)
        response = client.post(
            "/app/billing/subscriptions/{}/cancel/".format(subscription.pk)
        )
        assert response.status_code == 302
        subscription.refresh_from_db()
        assert subscription.status == "cancelled"
        assert subscription.end_date is not None

    def test_cancel_only_own_subscription(self, user, plan):
        from django.contrib.auth import get_user_model

        other = get_user_model().objects.create_user(
            email="other@example.com", password="testpass123!"
        )
        sub = Subscription.objects.create(
            user=other, plan=plan, status="active", gateway="dummy",
            gateway_subscription_id="other_sub",
        )
        client = Client()
        client.force_login(user)
        response = client.post(
            "/app/billing/subscriptions/{}/cancel/".format(sub.pk)
        )
        assert response.status_code == 404


@pytest.mark.django_db
def test_stripe_webhook():
    client = Client()
    response = client.post("/app/billing/stripe/webhook/", {},
                           content_type="application/json")
    assert response.status_code == 200
