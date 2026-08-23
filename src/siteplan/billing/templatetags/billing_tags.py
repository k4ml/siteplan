from django import template

from siteplan.billing.currency import format_price

register = template.Library()


@register.filter
def get_price(plan, currency):
    return plan.get_price(currency)


@register.filter
def price_display(price_entry):
    if not price_entry:
        return ""
    return format_price(price_entry["amount"], price_entry["currency"])
