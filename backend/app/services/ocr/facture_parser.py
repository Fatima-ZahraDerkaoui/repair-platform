import re


class FactureParser:

    @staticmethod
    def parse(texte):

        resultat = {}

        numero = re.search(
            r"FV\d{4}-\d+",
            texte
        )

        if numero:
            resultat["numero"] = numero.group()

        date = re.search(
            r"\d{2}/\d{2}/\d{4}",
            texte
        )

        if date:
            resultat["date"] = date.group()

        total_ttc = re.search(
            r"Total TTC.*?(\d+\s?\d*,\d+)",
            texte,
            re.S
        )

        if total_ttc:
            resultat["total_ttc"] = total_ttc.group(1)

        return resultat