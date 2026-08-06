class InvoiceDetector:

    HEADER_KEYWORDS = [

        "DESIGNATION",
        "DÉSIGNATION",
        "DESCRIPTION",
        "LIBELLE",
        "LIBELLÉ",
        "ARTICLE",
        "REFERENCE",
        "RÉFÉRENCE"

    ]

    FOOTER_KEYWORDS = [

        "TOTAL HT",
        "TOTAL H.T",
        "TOTAL TVA",
        "TOTAL TTC",
        "NET A PAYER",
        "NET À PAYER",
        "A PAYER",
        "À PAYER",
        "SOUS TOTAL",
        "SOUS-TOTAL",
        "MONTANT HT",
        "TOTAL GENERAL"

    ]

    HEADER_MARGIN = 8
    FOOTER_MARGIN = 8
    MIN_DISTANCE = 120

    # =====================================================

    @staticmethod
    def normalize(text):

        text = text.upper()

        replacements = {

            "É": "E",
            "È": "E",
            "Ê": "E",
            "Ë": "E",
            "À": "A",
            "Â": "A",
            "Ù": "U",
            "Û": "U",
            "Ô": "O",
            "Ö": "O",
            "Î": "I",
            "Ï": "I",
            "Ç": "C"

        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = " ".join(text.split())

        return text.strip()

    # =====================================================

    def detect(self, elements):

        header_y = None
        footer_y = None

        # -------------------------
        # HEADER
        # -------------------------

        for e in sorted(elements, key=lambda x: x["box"][1]):

            text = self.normalize(e["text"])

            x1, y1, x2, y2 = e["box"]

            center = (y1 + y2) / 2

            if any(k == text for k in map(self.normalize, self.HEADER_KEYWORDS)):

                header_y = center

                break

        if header_y is None:

            return None

        # -------------------------
        # FOOTER
        # -------------------------

        for e in sorted(elements, key=lambda x: x["box"][1]):

            x1, y1, x2, y2 = e["box"]

            center = (y1 + y2) / 2

            if center < header_y + self.MIN_DISTANCE:

                continue

            text = self.normalize(e["text"])

            if any(self.normalize(k) in text for k in self.FOOTER_KEYWORDS):

                footer_y = center

                break

        if footer_y is None:

            footer_y = float("inf")

        return {

            "header_y": header_y,
            "footer_y": footer_y

        }

    # =====================================================

    def extract_table_elements(self, elements):

        bounds = self.detect(elements)

        if bounds is None:

            return []

        top = bounds["header_y"] - self.HEADER_MARGIN

        bottom = bounds["footer_y"] + self.FOOTER_MARGIN

        resultat = []

        for e in elements:

            x1, y1, x2, y2 = e["box"]

            center = (y1 + y2) / 2

            if top <= center <= bottom:

                resultat.append(e)

        return resultat