from decimal import Decimal

CURRENCY_SYMBOLS = {
    "usd": "$",
    "eur": "\u20ac",
    "gbp": "\u00a3",
    "myr": "RM",
    "sgd": "S$",
    "jpy": "\u00a5",
    "aud": "A$",
    "cad": "C$",
    "inr": "\u20b9",
    "php": "\u20b1",
    "thb": "\u0e3f",
    "idr": "Rp",
    "krw": "\u20a9",
    "brl": "R$",
    "mxn": "MX$",
}


def get_currency_symbol(currency_code):
    return CURRENCY_SYMBOLS.get(currency_code.lower(), currency_code.upper() + " ")


def format_price(amount, currency_code):
    symbol = get_currency_symbol(currency_code)
    amount = Decimal(str(amount))
    return f"{symbol}{amount:.2f}"
