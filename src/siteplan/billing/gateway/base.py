class BaseGateway:
    def create_subscription(self, user, plan) -> dict:
        raise NotImplementedError

    def cancel_subscription(self, subscription) -> bool:
        raise NotImplementedError

    def handle_webhook(self, payload, signature) -> dict:
        raise NotImplementedError
