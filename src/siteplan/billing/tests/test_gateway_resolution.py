import pytest
from django.test import Client

from siteplan.billing.gateway.stripe import StripeGateway


class TestGatewayResolution:
    def test_get_gateway_dummy(self):
        from siteplan.billing.gateway import get_gateway
        from siteplan.billing.gateway.dummy import DummyGateway

        gateway = get_gateway()
        assert isinstance(gateway, DummyGateway)

    def test_get_gateway_stripe(self):
        from siteplan.billing.gateway import get_gateway
        from siteplan.billing.models import GatewayConfig

        config = GatewayConfig.load()
        config.active_gateway = "stripe"
        config.save()

        gateway = get_gateway()
        assert isinstance(gateway, StripeGateway)
