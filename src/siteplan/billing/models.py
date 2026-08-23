from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Plan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    prices = models.JSONField(default=list, blank=True)
    features = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Plan")
        verbose_name_plural = _("Plans")

    def __str__(self):
        return self.name

    def get_price(self, currency=None):
        if not self.prices:
            return None
        if currency is None:
            currency = getattr(settings, "BILLING_DEFAULT_CURRENCY", "usd")
        currency = currency.lower()
        for entry in self.prices:
            if entry.get("currency", "").lower() == currency:
                return entry
        return self.prices[0]

    def supported_currencies(self):
        return [p.get("currency", "") for p in self.prices if p.get("currency")]

    @property
    def prices_display(self):
        """Human-readable prices, e.g. '$10.00 USD, RM45.00 MYR'."""
        from .currency import format_price

        return ", ".join(
            format_price(p["amount"], p["currency"])
            for p in self.prices
            if p.get("currency") and p.get("amount")
        ) or "-"


class GatewayConfig(models.Model):
    class Gateway(models.TextChoices):
        DUMMY = "dummy", _("Dummy")
        STRIPE = "stripe", _("Stripe")

    active_gateway = models.CharField(
        max_length=20, choices=Gateway.choices, default=Gateway.DUMMY,
    )
    stripe_secret_key = models.CharField(max_length=255, blank=True)
    stripe_publishable_key = models.CharField(max_length=255, blank=True)
    stripe_webhook_secret = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _("Gateway Configuration")
        verbose_name_plural = _("Gateway Configuration")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        CANCELLED = "cancelled", _("Cancelled")
        EXPIRED = "expired", _("Expired")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.PROTECT, related_name="subscriptions",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE,
    )
    gateway = models.CharField(max_length=20)
    gateway_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status="active"),
                name="unique_active_subscription_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.plan.name}"
