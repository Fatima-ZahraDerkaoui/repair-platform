import re


class ArticleParser:

    @staticmethod
    def to_float(value):

        value = value.replace(" ", "")
        value = value.replace(",", ".")

        try:
            return float(value)
        except:
            return None

    @staticmethod
    def is_number(txt):

        return re.match(
            r"^[0-9]+([.,][0-9]+)?$",
            txt
        ) is not None

    @classmethod
    def parse_line(cls, ligne):

        ligne = sorted(
            ligne,
            key=lambda c: c["box"][0]
        )

        if len(ligne) < 4:
            return None

        # -----------------------------------------
        # Référence = premier bloc
        # -----------------------------------------

        reference = ligne[0]["text"].strip()

        if len(reference) < 3:
            return None

        textes = [c["text"] for c in ligne[1:]]

        designation = []

        tva = ""

        prix = None

        quantite = None

        total = None

        nombres = []

        # -----------------------------------------
        # Recherche TVA
        # -----------------------------------------

        for t in textes:

            if "%" in t:

                tva = t

                continue

            if cls.is_number(t):

                nombres.append(t)

            else:

                designation.append(t)

        # -----------------------------------------
        # Extraction des nombres
        # -----------------------------------------

        valeurs = []

        for n in nombres:

            v = cls.to_float(n)

            if v is not None:

                valeurs.append(v)

        if len(valeurs) >= 3:

            prix = valeurs[0]

            total = valeurs[-1]

            for v in valeurs:

                if float(v).is_integer():

                    q = int(v)

                    if 1 <= q <= 999:

                        quantite = q

                        break

        # -----------------------------------------
        # Nettoyage désignation
        # -----------------------------------------

        designation = " ".join(designation)

        designation = re.sub(
            r"\s+",
            " ",
            designation
        ).strip()

        return {

            "reference": reference,

            "designation": designation,

            "prix_unitaire": prix,

            "quantite": quantite,

            "tva": tva,

            "total": total

        }