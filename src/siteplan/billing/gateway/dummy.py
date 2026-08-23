from .base import BaseGateway


class DummyGateway(BaseGateway):
    def create_subscription(self, user, plan):
        return {"gateway_subscription_id": f"dummy_sub_{user.pk}_{plan.pk}"}

    def cancel_subscription(self, subscription):
        return True

    def handle_webhook(self, payload, signature):
        return {"type": "unhandled"}
