from siteplan.billing.models import GatewayConfig
from .dummy import DummyGateway
from .stripe import StripeGateway


def get_gateway():
    config = GatewayConfig.load()
    if config.active_gateway == GatewayConfig.Gateway.STRIPE:
        return StripeGateway(config)
    return DummyGateway()
