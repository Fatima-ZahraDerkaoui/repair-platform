# ============================================================
# CONFIGURATION & UTILITAIRES DOSSIERS
# ============================================================

API_URL = "http://127.0.0.1:8000"
DEFAULT_UTILISATEUR_ID = 1


def safe_int(value, default=0):
    try:
        return int(value or default)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value or default)
    except (ValueError, TypeError):
        return default


def format_money(value):
    try:
        if value is None:
            return "- DH"
        return f"{float(value):,.2f} DH".replace(",", " ")
    except (ValueError, TypeError):
        return "0.00 DH"


def format_date(value):
    if not value:
        return "-"
    return str(value).replace("T", " ")[:19]
