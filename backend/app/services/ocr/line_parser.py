import re

from app.services.ocr.models import LigneDocument


REFERENCE_REGEX = re.compile(
    r"^[A-Z]{2,}[A-Z0-9\-]*"
)


class LineParser:

    def parser(self, ocr_resultats):

        produits = []

        prix = []
        quantites = []

        for item in ocr_resultats:

            texte = item["text"].strip()

            x1, y1, x2, y2 = item["box"]

            ####################################################
            # PRODUITS
            ####################################################

            m = REFERENCE_REGEX.match(texte)

            if m:

                reference = m.group()

                designation = texte[len(reference):]

                designation = designation.replace("-", "").strip()

                produits.append(
                    {
                        "x": x1,
                        "reference": reference,
                        "designation": designation
                    }
                )

                continue

            ####################################################
            # PRIX
            ####################################################

            if re.fullmatch(r"\d+[.,]\d{2}", texte):

                prix.append(
                    {
                        "x": x1,
                        "valeur": float(
                            texte.replace(",", ".")
                        )
                    }
                )

                continue

            ####################################################
            # QUANTITE
            ####################################################

            if texte in ["1", "2", "3", "4", "5"]:

                quantites.append(
                    {
                        "x": x1,
                        "valeur": int(texte)
                    }
                )

        ####################################################
        # TRI
        ####################################################

        produits.sort(key=lambda p: p["x"])

        prix.sort(key=lambda p: p["x"])

        quantites.sort(key=lambda p: p["x"])

        ####################################################
        # ASSOCIATION
        ####################################################

        resultat = []

        for i, produit in enumerate(produits):

            pu = None
            qte = None
            total = None

            if i < len(prix):

                pu = prix[i]["valeur"]

            if i < len(quantites):

                qte = quantites[i]["valeur"]

            if pu is not None and qte is not None:

                total = pu * qte

            resultat.append(

                LigneDocument(

                    reference=produit["reference"],

                    designation=produit["designation"],

                    quantite=qte,

                    prix_unitaire=pu,

                    total=total

                )

            )

        return resultat