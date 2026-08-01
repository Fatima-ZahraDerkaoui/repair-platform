import re


class ArticleParser:

    @staticmethod
    def parse_line(ligne):

        ligne = sorted(

            ligne,

            key=lambda c: c["box"][0]

        )

        textes = [

            c["text"]

            for c in ligne

        ]

        if len(textes) < 5:
            return None

        reference = textes[0]

        if not re.match(

                r"^[A-Za-z0-9\-]+$",

                reference

        ):

            return None

        nombres = []

        designation = []

        started_numbers = False

        for token in textes[1:]:

            if re.match(

                    r"^[0-9]+([,.][0-9]+)?$",

                    token

            ):

                started_numbers = True

                nombres.append(token)

            else:

                if not started_numbers:

                    designation.append(token)

        if len(nombres) < 4:
            return None

        try:

            prix = float(

                nombres[0].replace(",", ".")

            )

        except:

            prix = None

        try:

            quantite = int(

                float(nombres[2])

            )

        except:

            quantite = 1

        try:

            total = float(

                nombres[3].replace(",", ".")

            )

        except:

            total = None

        return {

            "reference": reference,

            "designation": " ".join(designation),

            "prix_unitaire": prix,

            "quantite": quantite,

            "tva": nombres[1],

            "total": total

        } 