import re

# ==========================
# DOCUMENTS
# ==========================

FACTURE = re.compile(
    r"(?:FACTURE|BL/FACTURE)\s*(?:N°|NO|N)?\s*:?\s*([A-Z0-9\-]+)",
    re.IGNORECASE
)

BL = re.compile(
    r"BON\s+DE\s+LIVRAISON.*?(?:N°|NO)?\s*:?\s*([A-Z0-9\-]+)",
    re.IGNORECASE
)

AVOIR = re.compile(
    r"AVOIR.*?(?:N°|NO)?\s*:?\s*([A-Z0-9\-]+)",
    re.IGNORECASE
)

# ==========================
# DATE
# ==========================

DATE = re.compile(
    r"\d{2}/\d{2}/\d{4}"
)

# ==========================
# MONTANTS
# ==========================

MONTANT = re.compile(
    r"\d[\d\s]*[.,]\d{2}"
)

# ==========================
# REFERENCES ARTICLES
# ==========================

REFERENCE = re.compile(
    r"^[A-Z0-9]{2,}(?:-[A-Z0-9]+)+"
)