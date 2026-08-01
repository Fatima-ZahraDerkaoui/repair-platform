import re


class TableMerger:

    def merge(self, lignes):

        resultat = []

        courant = []

        for ligne in lignes:

            textes = [

                c["text"]

                for c in ligne

            ]

            texte = " ".join(textes)

            texte = texte.strip()

            if texte == "":
                continue

            debut_article = re.match(

                r"^[A-Z0-9\-]{4,}",

                textes[0]

            )

            if debut_article:

                if courant:
                    resultat.append(courant)

                courant = ligne

            else:

                courant.extend(ligne)

        if courant:
            resultat.append(courant)

        return resultat