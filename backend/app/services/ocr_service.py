from paddleocr import PaddleOCR
from pathlib import Path


ocr = PaddleOCR(
    lang="fr"
)


def traiter_document(
    chemin_fichier: str
):

    resultat = ocr.predict(
        chemin_fichier
    )

    textes = []

    for page in resultat:

        if not page:

            continue

        data = page.json

        if isinstance(data, dict):

            res = data.get(
                "res",
                {}
            )

            rec_texts = res.get(
                "rec_texts",
                []
            )

            textes.extend(
                rec_texts
            )

    texte_complet = "\n".join(
        textes
    )

    return {

        "texte": texte_complet,

        "type_document":
        classifier_document(
            texte_complet
        )

    }


def classifier_document(
    texte: str
):

    texte_lower = texte.lower()

    if any(

        mot in texte_lower

        for mot in [

            "facture",
            "invoice",
            "total ttc",
            "total ht"

        ]

    ):

        return "facture"


    if any(

        mot in texte_lower

        for mot in [

            "bon de livraison",
            "livraison",
            "quantité livrée"

        ]

    ):

        return "bon_livraison"


    if any(

        mot in texte_lower

        for mot in [

            "devis",
            "proforma"

        ]

    ):

        return "devis"


    return "inconnu"