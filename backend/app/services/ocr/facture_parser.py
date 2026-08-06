import re
from app.services.ocr.supplier_extractor import SupplierExtractor

class FactureParser:

    def __init__(self):

        self.supplier = SupplierExtractor()

    # ==================================================

    def extract_invoice_number(self, texte):

        patterns = [

            r"(?:FACTURE|INVOICE|BL\/FACTURE)\s*(?:N°|Nº|NO|NUMERO|NUMBER)?\s*[:\-]?\s*([A-Z0-9\-\/]+)",

            r"N°\s*[:\-]?\s*([A-Z0-9\-\/]+)",

            r"NO\s*[:\-]?\s*([A-Z0-9\-\/]+)"
        ]

        texte = texte.upper()

        for pattern in patterns:

            match = re.search(pattern, texte)

            if match:
                return match.group(1).strip()

        return None

    # ==================================================

    def extract_date(self, texte):

        texte = texte.upper()

        patterns = [

            r"DATE\s+FACTURATION\s*[:\-]?\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})",

            r"DATE\s+FACTURE\s*[:\-]?\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})",

            r"DATE\s+EMISSION\s*[:\-]?\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})",

            r"INVOICE\s+DATE\s*[:\-]?\s*(\d{4}[\/\-\.]\d{2}[\/\-\.]\d{2})",

            r"DATE\s*[:\-]?\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})",

            r"(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})"

        ]

        for pattern in patterns:

            match = re.search(pattern, texte)

            if match:
                return match.group(1)

        return None

    # ==================================================

    def extract_client(self, texte):

        lines = [
            line.strip()
            for line in texte.splitlines()
            if line.strip()
        ]

        keywords = [

            "CLIENT",
            "DESTINATAIRE",
            "LIVRER",
            "LIVRAISON",
            "ADRESSE CLIENT",
            "SOCIETE"

        ]

        for i, line in enumerate(lines):

            upper = line.upper()

            if any(k in upper for k in keywords):

                # regarde les 3 lignes suivantes
                for j in range(i + 1, min(i + 4, len(lines))):

                    candidate = lines[j]

                    if len(candidate) < 3:
                        continue

                    if any(c.isalpha() for c in candidate):

                        return candidate

        return None

    # ==================================================
    """ 
    def extract_supplier(self, texte):

        lines = [
            line.strip()
            for line in texte.splitlines()
            if line.strip()
        ]

        stop_words = [

            "FACTURE",
            "BL/FACTURE",
            "DATE",
            "TEL",
            "ICE",
            "IF",
            "RC",
            "PATENTE",
            "CLIENT",
            "DESTINATAIRE"

        ]

        for line in lines[:12]:

            upper = line.upper()

            if any(word in upper for word in stop_words):
                continue

            if len(line) < 3:
                continue

            if any(c.isalpha() for c in line):

                return line

        return None
    """
    # ==================================================
    def extract_totals(self, texte):

        texte = texte.upper()

        totals = {
            "total_ht": None,
            "total_tva": None,
            "total_ttc": None
        }

        patterns = {

            "total_ht": [

                r"TOTAL\s+H\.?T\.?\s*([0-9 ]+[.,][0-9]{2})",
                r"SOUS[- ]?TOTAL\s*([0-9 ]+[.,][0-9]{2})",

            ],

            "total_tva": [

                r"TOTAL\s+TVA(?:\s+\d+%)?\s*([0-9 ]+[.,][0-9]{2})",

            ],

            "total_ttc": [

                r"TOTAL\s+TTC\s*([0-9 ]+[.,][0-9]{2})",
                r"NET\s+A\s+PAYER\s*([0-9 ]+[.,][0-9]{2})",
                r"A\s+PAYER\s*([0-9 ]+[.,][0-9]{2})",

            ]

        }

        for key, plist in patterns.items():

            for pattern in plist:

                m = re.search(pattern, texte)

                if m:

                    value = (
                        m.group(1)
                        .replace(" ", "")
                        .replace(",", ".")
                    )

                    try:
                        totals[key] = float(value)
                    except:
                        pass

                    break

        return totals

    # ==================================================
    """
    def extract_tax_information(self, texte):

        texte = texte.upper()

        taxes = {
            "ice": None,
            "if": None,
            "rc": None,
            "patente": None,
            "cnss": None
        }

        patterns = {

            "ice": [

                r"ICE\s*[:.]?\s*([0-9]{10,20})",

                r"I\.?C\.?E\.?\s*[:.]?\s*([0-9]{10,20})"

            ],

            "if": [

                r"\bIF\b\s*[:.]?\s*([0-9]{4,15})",

                r"I\.?F\.?\s*[:.]?\s*([0-9]{4,15})"

            ],

            "rc": [

                r"\bRC\b\s*[:.]?\s*([0-9]{2,15})",

                r"R\.?C\.?\s*[:.]?\s*([0-9]{2,15})"

            ],

            "patente": [

                r"PATENTE\s*[:.]?\s*([0-9]{4,20})"

            ],

            "cnss": [

                r"CNSS\s*[:.]?\s*([0-9]{4,20})"

            ]

        }

        for field, plist in patterns.items():

            for pattern in plist:

                m = re.search(pattern, texte)

                if m:

                    taxes[field] = m.group(1)

                    break

        return taxes
    """
    # ==================================================
    def parse(self, texte, articles):

        data = {}

        data["numero"] = self.extract_invoice_number(texte)

        data["date"] = self.extract_date(texte)

        data["client"] = self.extract_client(texte)

        data.update(
            self.extract_totals(texte)
        )

        data["fournisseur"] = self.supplier.extract(texte)

        data["articles"] = articles

        return data
