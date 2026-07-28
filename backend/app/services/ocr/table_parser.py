import re

REFERENCE_REGEX = re.compile(
    r"^[A-Z]{2,}[A-Z0-9\-]+"
)

def est_ligne_produit(ligne):

    for cellule in ligne:

        texte = cellule["text"]

        if REFERENCE_REGEX.match(texte):

            return True

    return False