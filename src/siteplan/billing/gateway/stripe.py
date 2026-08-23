from .base import BaseGateway


class StripeGateway(BaseGateway):
    def __init__(self, config):
        self.config = config

    def create_checkout_session(self, user, plan, success_url, cancel_url):
        pass

    def create_subscription(self, user, plan):
        return {"gateway_subscription_id": f"stripe_sub_{user.pk}_{plan.pk}"}

    def cancel_subscription(self, subscription):
        return True

    def handle_webhook(self, payload, signature):
        return {"type": "unhandled"}
