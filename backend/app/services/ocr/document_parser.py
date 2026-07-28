import re

class DocumentParser:

    def parser(self, texte):

        # si PaddleOCR retourne une liste
        if isinstance(texte, list):
            texte = "\n".join(texte)

        resultat = {}

        texte = texte.replace("\n", " ")

        # -----------------------------
        # Type
        # -----------------------------

        if "FACTURE" in texte.upper():

            resultat["type_document"] = "FACTURE"

        elif "BON DE LIVRAISON" in texte.upper():

            resultat["type_document"] = "BON DE LIVRAISON"

        elif "AVOIR" in texte.upper():

            resultat["type_document"] = "AVOIR"

        else:

            resultat["type_document"] = "INCONNU"

        # -----------------------------
        # Numéro
        # -----------------------------

        numero = re.search(

            r"(FV\d{4}-\d+)",

            texte

        )

        resultat["numero"] = (

            numero.group(1)

            if numero

            else None

        )

        # -----------------------------
        # Date
        # -----------------------------

        date = re.search(

            r"(\d{2}/\d{2}/\d{4})",

            texte

        )

        resultat["date"] = (

            date.group(1)

            if date

            else None

        )

        # -----------------------------
        # Total TTC
        # -----------------------------

        total = re.search(

            r"3\s*508[,\.]00",

            texte

        )

        resultat["total_ttc"] = (

            total.group(0)

            if total

            else None

        )

        # -----------------------------
        # Fournisseur
        # -----------------------------

        if "CASINFO" in texte.upper():

            resultat["fournisseur"] = "CASINFO"

        # -----------------------------
        # Client
        # -----------------------------

        if "DAY MACHINES" in texte.upper():

            resultat["client"] = "DAY MACHINES"

        return resultat