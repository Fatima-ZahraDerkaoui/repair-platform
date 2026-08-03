from collections import defaultdict
import re


class LineBuilder:

    def __init__(self, tolerance_y=15):
        self.tolerance_y = tolerance_y

    # ----------------------------------------------------
    def group_by_y(self, elements):

        rows = defaultdict(list)

        for e in elements:

            x1, y1, x2, y2 = e["box"]

            centre_y = (y1 + y2) / 2

            key = round(centre_y / self.tolerance_y)

            rows[key].append(e)

        lignes = []

        for _, row in sorted(rows.items()):

            row = sorted(row, key=lambda x: x["box"][0])

            lignes.append(row)

        return lignes

    # ----------------------------------------------------
    def is_reference(self, texte):

        texte = texte.upper().strip()

        prefixes = (
            "HP",
            "EPST",
            "CANGI",
            "CAN",
            "BRO",
            "LEX",
            "OKI",
            "KYO",
            "RIC",
            "XER",
            "PAN",
            "SAM",
            "TOS"
        )

        return any(texte.startswith(p) for p in prefixes)

    # ----------------------------------------------------
    def is_total(self, texte):

        return "TOTAL HT" in texte.upper()

    # ----------------------------------------------------
    def build(self, elements):

        lignes = self.group_by_y(elements)

        resultat = []

        started = False

        article = None

        for ligne in lignes:

            textes = [c["text"] for c in ligne]

            texte = " ".join(textes)

            upper = texte.upper()

            # ----------------------------
            # début du tableau
            # ----------------------------

            if "DESIGNATION" in upper or "DÉSIGNATION" in upper:

                started = True
                continue

            if not started:
                continue

            # ----------------------------
            # fin du tableau
            # ----------------------------

            if self.is_total(upper):

                if article:

                    resultat.append(article)

                    article = None

                break

            # ----------------------------
            # nouvelle référence
            # ----------------------------

            if self.is_reference(textes[0]):

                if article:

                    resultat.append(article)

                article = ligne.copy()

            else:

                if article:

                    texte = " ".join(c["text"] for c in ligne).upper()

                    # Fin du tableau
                    if (
                        "N°SENE" in texte
                        or "MAGASINIER" in texte
                        or "TOTAL HT" in texte
                        or "TOTAL TVA" in texte
                        or "TOTAL TTC" in texte
                    ):
                        resultat.append(article)
                        article = None
                        break

                    article.extend(ligne)

        if article:

            resultat.append(article)

        # ----------------------------
        # tri final
        # ----------------------------

        for ligne in resultat:

            ligne.sort(

                key=lambda x: x["box"][0]

            )

        return resultat
    