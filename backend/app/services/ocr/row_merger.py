import re


REFERENCE_REGEX = re.compile(
    r"^[A-Z]{2,}[A-Z0-9\-]+"
)


class RowMerger:

    def merge(self, lignes):

        resultat = []

        i = 0

        while i < len(lignes):

            ligne = lignes[i]

            if self.est_produit(ligne):

                produit = list(ligne)

                j = i + 1

                while j < len(lignes):

                    suivante = lignes[j]

                    if self.est_produit(suivante):

                        break

                    produit.extend(suivante)

                    j += 1

                resultat.append(produit)

                i = j

            else:

                i += 1

        return resultat

    def est_produit(self, ligne):

        for cellule in ligne:

            texte = cellule["text"]

            if REFERENCE_REGEX.match(texte):

                return True

        return False