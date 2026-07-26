from django import forms
from django.utils.translation import gettext_lazy as _

from .models import GatewayConfig


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
