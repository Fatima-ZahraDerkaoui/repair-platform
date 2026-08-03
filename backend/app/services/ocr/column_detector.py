import re
import unicodedata


class ColumnDetector:

    HEADERS = {

        "reference": [
            "REFERENCE",
            "RÉFÉRENCE",
            "REF",
            "REF.",
            "CODE",
            "CODE ARTICLE",
            "N ARTICLE",
            "ARTICLE",
            "SKU",
            "ITEM",
            "ITEM CODE",
            "PRODUCT CODE"
        ],

        "designation": [
            "DESIGNATION",
            "DÉSIGNATION",
            "DESCRIPTION",
            "LIBELLE",
            "LIBELLÉ",
            "PRODUIT",
            "ARTICLE",
            "ITEM",
            "DESCRIPTIF",
            "DESIGNATION ARTICLE"
        ],

        "qte": [
            "QTE",
            "QTÉ",
            "QUANTITE",
            "QUANTITÉ",
            "QTY",
            "NBR",
            "NB",
            "PCS",
            "PIECES",
            "UNITES"
        ],

        "pu": [
            "PU",
            "P.U",
            "P.U.",
            "P.U HT",
            "P.U TTC",
            "PRIX",
            "PRIX HT",
            "PRIX TTC",
            "PRIX UNITAIRE",
            "UNIT PRICE",
            "UNIT COST"
        ],

        "remise": [
            "REMISE",
            "REM",
            "DISCOUNT",
            "REDUCTION",
            "RABAIS"
        ],

        "tva": [
            "TVA",
            "VAT",
            "TAXE",
            "TAX"
        ],

        "total": [
            "TOTAL",
            "TOTAL HT",
            "TOTAL TTC",
            "MONTANT",
            "MONTANT TTC",
            "NET TTC",
            "AMOUNT",
            "LINE TOTAL"
        ]
    }

    # -----------------------------------------------------

    def normalize(self, text):

        text = text.upper()

        text = unicodedata.normalize("NFD", text)

        text = "".join(
            c for c in text
            if unicodedata.category(c) != "Mn"
        )

        text = re.sub(r"[^A-Z0-9 ]", " ", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # -----------------------------------------------------

    def detect(self, elements):

        candidats = {}

        for e in elements:

            texte = self.normalize(e["text"])

            x1, y1, x2, y2 = e["box"]

            centre = (x1 + x2) / 2

            largeur = x2 - x1

            score = e.get("score", 1)

            for colonne, aliases in self.HEADERS.items():

                for alias in aliases:

                    alias = self.normalize(alias)

                    if alias == texte or alias in texte:

                        poids = score * largeur

                        if (
                            colonne not in candidats
                            or poids > candidats[colonne]["poids"]
                        ):

                            candidats[colonne] = {

                                "x": centre,

                                "poids": poids,

                                "texte": texte

                            }

        colonnes = {}

        for nom, info in candidats.items():

            colonnes[nom] = info["x"]

        return colonnes
    