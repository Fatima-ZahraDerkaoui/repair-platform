class DocumentClassifier:

    @staticmethod
    def detecter(texte: str):

        texte = texte.upper()

        if "FACTURE" in texte:
            return "FACTURE"

        if "BON DE LIVRAISON" in texte:
            return "BON_LIVRAISON"

        if "AVOIR" in texte:
            return "AVOIR"

        return "INCONNU"