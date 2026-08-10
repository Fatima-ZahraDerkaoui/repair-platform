import re
from app.services.ocr.supplier_extractor import SupplierExtractor


class FactureParser:
    """Extracts invoice-level information independently of table layout."""

    def __init__(self):
        self.supplier = SupplierExtractor()

    @staticmethod
    def normalize(text):
        if text is None:
            return ""
        text = str(text).upper()
        replacements = str.maketrans({
            "É": "E", "È": "E", "Ê": "E", "Ë": "E",
            "À": "A", "Â": "A", "Ç": "C",
            "Ù": "U", "Û": "U", "Ô": "O", "Ö": "O",
            "Î": "I", "Ï": "I",
        })
        return re.sub(r"\s+", " ", text.translate(replacements)).strip()

    @staticmethod
    def parse_amount(value):
        if value is None:
            return None
        value = str(value).strip().replace(" ", "")
        if "," in value and "." in value:
            if value.rfind(",") > value.rfind("."):
                value = value.replace(".", "").replace(",", ".")
            else:
                value = value.replace(",", "")
        else:
            value = value.replace(",", ".")
        try:
            return float(value)
        except ValueError:
            return None

    def extract_invoice_number(self, texte):

        texte = texte.upper()

        patterns = [

            # FACTURE N° FAC 26M/00529
            r"(?:FACTURE|INVOICE|BL/FACTURE)"
            r"\s*(?:N°|Nº|NO|NUMERO|NUMBER)?"
            r"\s*[:\-]?\s*"
            r"([A-Z]{1,10}\s*[A-Z0-9]+(?:[\/\-][A-Z0-9]+)+)",

            # FACTURE N° 12345
            r"(?:FACTURE|INVOICE)"
            r"\s*(?:N°|Nº|NO|NUMERO|NUMBER)"
            r"\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9\/\-]+)",

            # N° FAC 26M/00529
            r"N°\s*[:\-]?\s*"
            r"([A-Z]{1,10}\s*[A-Z0-9]+(?:[\/\-][A-Z0-9]+)+)",

            # NO FAC-123
            r"\bNO\b\s*[:\-]?\s*"
            r"([A-Z0-9][A-Z0-9\/\-]+)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                texte
            )

            if match:

                numero = match.group(1).strip()

                numero = re.sub(
                    r"\s+",
                    " ",
                    numero
                )

                return numero

        return None

    def extract_date(self, texte):
        texte = self.normalize(texte)
        patterns = [
            r"DATE\s+FACTURATION\s*[:\-]?\s*(\d{2}[/.\-]\d{2}[/.\-]\d{4})",
            r"DATE\s+FACTURE\s*[:\-]?\s*(\d{2}[/.\-]\d{2}[/.\-]\d{4})",
            r"DATE\s+EMISSION\s*[:\-]?\s*(\d{2}[/.\-]\d{2}[/.\-]\d{4})",
            r"INVOICE\s+DATE\s*[:\-]?\s*(\d{4}[/.\-]\d{2}[/.\-]\d{2})",
            r"DATE\s*[:\-]?\s*(\d{2}[/.\-]\d{2}[/.\-]\d{4})",
            r"\b(\d{2}[/.\-]\d{2}[/.\-]\d{4})\b",
        ]
        for pattern in patterns:
            m = re.search(pattern, texte)
            if m:
                return m.group(1)
        return None

    def extract_client(self, texte):
        lines = [line.strip() for line in str(texte).splitlines() if line.strip()]
        keywords = ["CLIENT", "DESTINATAIRE", "LIVRER", "LIVRAISON", "ADRESSE CLIENT", "SOCIETE"]
        forbidden = ["FACTURE", "DATE", "TOTAL", "TVA", "TEL", "ICE", "IF", "RC"]
        for i, line in enumerate(lines):
            upper = self.normalize(line)
            if any(k in upper for k in keywords):
                for candidate in lines[i + 1:i + 4]:
                    c = candidate.strip()
                    cu = self.normalize(c)
                    if len(c) >= 3 and any(ch.isalpha() for ch in c) and not any(w in cu for w in forbidden):
                        return c
        return None

    def extract_totals(self, texte):

        texte = texte.upper()

        totals = {
            "total_ht": None,
            "total_tva": None,
            "total_ttc": None
        }

        # ======================================================
        # NORMALISATION
        # ======================================================

        texte = texte.replace(
            "\u00a0",
            " "
        )

        texte = re.sub(
            r"[ \t]+",
            " ",
            texte
        )

        # ======================================================
        # CONVERTISSEUR
        # ======================================================

        def parse_amount(value):

            if not value:
                return None

            value = value.strip()

            value = value.replace(
                " ",
                ""
            )

            if "," in value and "." in value:

                if value.rfind(",") > value.rfind("."):

                    value = value.replace(
                        ".",
                        ""
                    )

                    value = value.replace(
                        ",",
                        "."
                    )

                else:

                    value = value.replace(
                        ",",
                        ""
                    )

            else:

                value = value.replace(
                    ",",
                    "."
                )

            try:
                return float(value)

            except (
                ValueError,
                TypeError
            ):
                return None

        # ======================================================
        # PATTERNS
        # ======================================================

        patterns = {

            "total_ht": [

                r"TOTAL\s*H\.?\s*T\.?"
                r"\s*[:\-]?\s*"
                r"([0-9][0-9\s.,]*)",

                r"TOTAL\s+HT"
                r"\s*[:\-]?\s*"
                r"([0-9][0-9\s.,]*)",

                r"SOUS[- ]?TOTAL"
                r"(?:\s+HT)?"
                r"\s*[:\-]?\s*"
                r"([0-9][0-9\s.,]*)"
            ],

            "total_tva": [

                r"TOTAL\s*TVA"
                r"(?:\s+\d+(?:[.,]\d+)?\s*%)?"
                r"\s*[:\-]?\s*"
                r"([0-9][0-9\s.,]*)",

                r"TVA"
                r"\s*[:\-]?\s*"
                r"([0-9][0-9\s.,]*)"
            ],

            "total_ttc": [

                r"TOTAL\s*TTC"
                r"\s*[:\-]?\s*"
                r"([0-9][0-9\s.,]*)",

                r"NET\s+A\s+PAYER"
                r"\s*[:\-]?\s*"
                r"([0-9][0-9\s.,]*)",

                r"A\s+PAYER"
                r"\s*[:\-]?\s*"
                r"([0-9][0-9\s.,]*)"
            ]
        }

        # ======================================================
        # EXTRACTION
        # ======================================================

        for key, pattern_list in patterns.items():

            for pattern in pattern_list:

                match = re.search(
                    pattern,
                    texte
                )

                if not match:
                    continue

                value = parse_amount(
                    match.group(1)
                )

                if value is not None:

                    totals[key] = value

                    break

        return totals

    def parse(self, texte, articles):
        texte = texte or ""
        data = {
            "numero": self.extract_invoice_number(texte),
            "date": self.extract_date(texte),
            "client": self.extract_client(texte),
            "fournisseur": self.supplier.extract(texte),
            "articles": articles or [],
        }
        data.update(self.extract_totals(texte))
        return data
    