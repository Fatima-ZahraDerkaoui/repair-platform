import re


def nettoyer(texte: str):

    texte = texte.replace("\n", " ")

    texte = re.sub(
        r"\s+",
        " ",
        texte
    )

    return texte.strip()


def chercher(pattern, texte):

    resultat = pattern.search(texte)

    if resultat:
        return resultat.group(1)

    return None


def convertir_prix(valeur):

    valeur = valeur.replace(" ", "")
    valeur = valeur.replace(",", ".")

    try:
        return float(valeur)
    except:
        return None