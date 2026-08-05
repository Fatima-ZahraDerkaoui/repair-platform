import re


class ArticleParser:

    # =====================================================

    def to_float(self, text):

        if not text:
            return None

        text = text.replace(" ", "")
        text = text.replace(",", ".")

        try:
            return float(text)
        except:
            return None

    # =====================================================

    def split_reference(self, text):

        text = text.strip()

        if not text:
            return "", ""

        morceaux = text.split("-")

        # Cas :
        # HP-F6V25AE-Cartouche HP 652 Black

        if len(morceaux) >= 3:

            reference = "-".join(morceaux[:2])

            designation = "-".join(morceaux[2:])

            return reference.strip(), designation.strip()

        # Cas :
        # CANGI490Y-CARTOUCHE CANON

        if len(morceaux) == 2:

            gauche = morceaux[0].strip()
            droite = morceaux[1].strip()

            # Si la partie gauche contient des chiffres,
            # c'est probablement la référence.

            if any(c.isdigit() for c in gauche):

                return gauche, droite

        # Cas :
        # REF123 Cartouche HP

        mots = text.split()

        if mots and any(c.isdigit() for c in mots[0]):

            return mots[0], " ".join(mots[1:])

        return "", text

    # =====================================================

    def parse_line(self, ligne):

        article = {

            "reference": "",

            "designation": "",

            "quantite": None,

            "prix_unitaire": None,

            "tva": None,

            "total": None

        }

        designation = []

        for cellule in ligne:

            colonne = cellule["column"]

            texte = cellule["text"]

            # --------------------------

            if colonne == "designation":

                designation.append(texte)

            elif colonne == "qte":

                article["quantite"] = int(float(texte))

            elif colonne == "pu":

                article["prix_unitaire"] = self.to_float(texte)

            elif colonne == "tva":

                article["tva"] = self.to_float(

                    texte.replace("%", "")

                )

            elif colonne == "total":

                article["total"] = self.to_float(texte)

        designation = " ".join(designation)

        ref, des = self.split_reference(designation)

        article["reference"] = ref

        article["designation"] = des

        return article

    # =====================================================

    def parse(self, lignes):

        articles = []

        for ligne in lignes:

            article = self.parse_line(ligne)

            if article["designation"]:

                articles.append(article)

        return articles