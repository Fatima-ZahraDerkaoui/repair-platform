# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"

# À remplacer plus tard par l'utilisateur connecté.
DEFAULT_UTILISATEUR_ID = 1

# ============================================================
# UTILITAIRES DOSSIERS
# ============================================================


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

        return f"{float(value or 0):,.2f} DH".replace(",", " ")

    except (ValueError, TypeError):

        return "0.00 DH"


def format_date(value):

    if not value:

        return "-"

    return str(value).replace("T", " ")[:19]