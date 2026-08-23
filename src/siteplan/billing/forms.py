import json

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import GatewayConfig, Plan


class PlanForm(forms.ModelForm):
    features = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": _("One feature per line")}
        ),
        help_text=_("Enter one feature per line."),
    )
    prices = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": _("usd 10.00\nmyr 45.00")}
        ),
        help_text=_("Enter one price per line: currency code then amount."),
    )

    class Meta:
        model = Plan
        fields = ["name", "description", "prices", "features", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance:
            self.initial["features"] = "\n".join(instance.features or [])
            self.initial["prices"] = "\n".join(
                f"{p['currency']} {p['amount']}"
                for p in instance.prices
                if p.get("currency") and p.get("amount")
            )

    def _parse_lines(self, value):
        return [
            line.strip()
            for line in (value or "").splitlines()
            if line.strip()
        ]

    def clean_features(self):
        return self._parse_lines(self.cleaned_data["features"])

    def clean_prices(self):
        result = []
        for line in self._parse_lines(self.cleaned_data["prices"]):
            parts = line.split()
            if len(parts) < 2:
                raise forms.ValidationError(
                    _("Invalid price format. Expected: currency amount (e.g. usd 10.00)")
                )
            result.append({
                "currency": parts[0].lower(),
                "amount": parts[1],
                "stripe_price_id": None,
            })
        return result


class GatewayConfigForm(forms.ModelForm):
    class Meta:
        model = GatewayConfig
        fields = [
            "active_gateway",
            "stripe_secret_key",
            "stripe_publishable_key",
            "stripe_webhook_secret",
        ]
        widgets = {
            "stripe_secret_key": forms.PasswordInput(render_value=True),
            "stripe_webhook_secret": forms.PasswordInput(render_value=True),
        }
