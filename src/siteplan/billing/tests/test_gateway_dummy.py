import pytest

from siteplan.billing.gateway.dummy import DummyGateway


class TestDummyGateway:
    def test_create_subscription(self, user, plan):
        gateway = DummyGateway()
        result = gateway.create_subscription(user, plan)
        assert result["gateway_subscription_id"] == f"dummy_sub_{user.pk}_{plan.pk}"

    def test_cancel_subscription(self, subscription):
        gateway = DummyGateway()
        assert gateway.cancel_subscription(subscription) is True

    def test_handle_webhook(self):
        gateway = DummyGateway()
        assert gateway.handle_webhook(b"", "") == {"type": "unhandled"}
