class InvoiceDetector:

    HEADER_KEYWORDS = [

        "DESIGNATION",
        "DÉSIGNATION",
        "DESCRIPTION",
        "LIBELLE",
        "LIBELLÉ"

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
        "SOUS-TOTAL"

    ]

    # ------------------------------------------------------------

    @staticmethod
    def normalize(text):

        text = text.upper()

        text = (
            text.replace("É", "E")
                .replace("È", "E")
                .replace("Ê", "E")
                .replace("À", "A")
                .replace("Ç", "C")
        )

        return text.strip()

    # ------------------------------------------------------------

    def detect(self, elements):

        header_y = None
        footer_y = None

        # ============================
        # Détection du header
        # ============================

        for e in elements:

            text = self.normalize(e["text"])

            x1, y1, x2, y2 = e["box"]

            center_y = (y1 + y2) / 2

            for keyword in self.HEADER_KEYWORDS:

                if self.normalize(keyword) == text:

                    header_y = center_y

                    break

            if header_y is not None:
                break

        # ============================
        # Header introuvable
        # ============================

        if header_y is None:

            return None

        # ============================
        # Détection du footer
        # ============================

        MIN_DISTANCE = 120

        for e in elements:

            x1, y1, x2, y2 = e["box"]

            center_y = (y1 + y2) / 2

            if center_y < header_y + MIN_DISTANCE:

                continue

            text = self.normalize(e["text"])

            for keyword in self.FOOTER_KEYWORDS:

                if self.normalize(keyword) in text:

                    footer_y = center_y

                    break

            if footer_y is not None:

                break

        if footer_y is None:

            footer_y = 999999

        return {

            "header_y": header_y,

            "footer_y": footer_y

        }

    # ------------------------------------------------------------

    def extract_table_elements(self, elements):

        bounds = self.detect(elements)

        if bounds is None:

            return []

        header_y = bounds["header_y"]

        footer_y = bounds["footer_y"]

        resultat = []

        for e in elements:

            x1, y1, x2, y2 = e["box"]

            center_y = (y1 + y2) / 2

            if header_y <= center_y <= footer_y:

                resultat.append(e)

        return resultat