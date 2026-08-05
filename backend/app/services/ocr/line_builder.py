from collections import defaultdict
import re


class LineBuilder:

    def __init__(self, tolerance_y=15):

        self.tolerance_y = tolerance_y

        # -----------------------------
        # Mots à ignorer (entêtes)
        # -----------------------------

        self.headers = {

            "DESIGNATION",
            "DÉSIGNATION",
            "REFERENCE",
            "RÉFÉRENCE",
            "REF",
            "ARTICLE",
            "TVA",
            "PU",
            "P.U",
            "P.U.",
            "P.U.TTC",
            "P.U HT",
            "PRIX",
            "PRIX UNITAIRE",
            "QTE",
            "QTÉ",
            "QUANTITE",
            "QUANTITÉ",
            "TOTAL",
            "TOTAL TTC",
            "REMISE"

        }

        # -----------------------------
        # Début d'une référence produit
        # -----------------------------

        self.reference_regex = re.compile(
            r"^[A-Z0-9][A-Z0-9\-/]{3,}$",
            re.IGNORECASE
        )

        # -----------------------------
        # Fin des articles
        # -----------------------------

        self.stop_words = [

            "TOTAL HT",
            "TOTAL TVA",
            "TOTAL TTC",
            "NET A PAYER",
            "MAGASINIER",
            "N°SENE",
            "N°SERIE",
            "N° SENE",
            "N° SERIE",
            "ARRETEE",
            "ARRÊTÉE",
            "TELEPHONE",
            "TÉLÉPHONE",
            "FAX",
            "ICE",
            "CNSS",
            "PATENTE",
            "R.C",
            "IF"

        ]

    # --------------------------------------------------------

    def normalize(self, text):

        text = text.upper()

        text = (
            text.replace("É", "E")
                .replace("È", "E")
                .replace("Ê", "E")
                .replace("À", "A")
                .replace("Ç", "C")
        )

        return text.strip()

    # --------------------------------------------------------

    def is_header(self, text):

        return self.normalize(text) in self.headers

    # --------------------------------------------------------

    def is_reference(self, text):

        return self.reference_regex.match(text) is not None

    # --------------------------------------------------------

    def is_stop(self, text):

        text = self.normalize(text)

        for word in self.stop_words:

            if self.normalize(word) in text:

                return True

        return False

    # --------------------------------------------------------

    def build(self, classified):

        # ============================
        # suppression des entêtes
        # ============================

        elements = []

        for e in classified:

            if self.is_header(e["text"]):
                continue

            elements.append(e)

        # ============================
        # regroupement par Y
        # ============================

        rows = defaultdict(list)

        for e in elements:

            key = round(e["y"] / self.tolerance_y)

            rows[key].append(e)

        grouped = []

        for _, row in sorted(rows.items()):

            row.sort(key=lambda x: x["x"])

            grouped.append(row)

        # ============================
        # Construction intelligente
        # ============================

        resultat = []

        article = None

        for row in grouped:

            texte = " ".join(c["text"] for c in row)

            if self.is_stop(texte):

                if article is not None:

                    resultat.append(article)

                    article = None

                break

            premier = row[0]["text"]

            if self.is_reference(premier):

                if article is not None:

                    resultat.append(article)

                article = row.copy()

            else:

                if article is not None:

                    article.extend(row)

        if article is not None:

            resultat.append(article)

        return resultat