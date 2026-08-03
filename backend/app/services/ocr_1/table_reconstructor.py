import re


class TableReconstructor:

    def __init__(self):
        pass

    @staticmethod
    def _center_x(cell):
        x1, y1, x2, y2 = cell["box"]
        return (x1 + x2) / 2

    @staticmethod
    def _is_reference(text):

        return re.match(
            r"^(HP|EPST|CAN|BRO|LEX|RIC|XER|OKI|KYO|PAN|TOS|SAM|EPS)",
            text.upper()
        ) is not None

    @staticmethod
    def _is_number(text):

        return re.match(
            r"^[0-9\s,.]+$",
            text
        ) is not None

    def reconstruct(self, lignes, colonnes):

        articles = []

        started = False

        current = None

        for ligne in lignes:

            textes = [
                c["text"]
                for c in ligne
            ]

            texte = " ".join(textes)

            upper = texte.upper()

            # =====================================================
            # Début du tableau
            # =====================================================

            if "DESIGNATION" in upper or "DÉSIGNATION" in upper:

                started = True
                continue

            if not started:
                continue

            # =====================================================
            # Fin du tableau
            # =====================================================

            if "TOTAL HT" in upper:
                break

            # =====================================================
            # Colonnes
            # =====================================================

            reference = ""

            designation = []

            tva = ""

            pu = ""

            qte = ""

            total = ""

            for cell in ligne:

                txt = cell["text"]

                x = self._center_x(cell)

                # -------------------------
                # TVA
                # -------------------------

                if (
                    colonnes["tva"] is not None
                    and abs(x - colonnes["tva"]) < 60
                ):

                    if "%" in txt:

                        tva = txt
                        continue

                # -------------------------
                # Prix
                # -------------------------

                if (
                    colonnes["prix"] is not None
                    and abs(x - colonnes["prix"]) < 70
                ):

                    if self._is_number(txt):

                        pu = txt
                        continue

                # -------------------------
                # Quantité
                # -------------------------

                if (
                    colonnes["qte"] is not None
                    and abs(x - colonnes["qte"]) < 50
                ):

                    if txt.isdigit():

                        qte = txt
                        continue

                # -------------------------
                # Total
                # -------------------------

                if (
                    colonnes["total"] is not None
                    and abs(x - colonnes["total"]) < 90
                ):

                    if self._is_number(txt):

                        total = txt
                        continue

                # -------------------------
                # Référence / Désignation
                # -------------------------

                if reference == "":

                    reference = txt

                else:

                    designation.append(txt)

            # =====================================================
            # Nouvelle référence
            # =====================================================

            if self._is_reference(reference):

                if current is not None:

                    articles.append(current)

                current = {

                    "reference": reference,

                    "designation": " ".join(designation),

                    "tva": tva,

                    "pu": pu,

                    "qte": qte,

                    "total": total

                }

            # =====================================================
            # Ligne suivante = suite de désignation
            # =====================================================

            else:

                if current is not None:

                    morceau = " ".join(

                        [reference] + designation

                    ).strip()

                    if morceau != "":

                        current["designation"] += " " + morceau

            # =====================================================
            # Mise à jour automatique si la suite contient
            # les colonnes manquantes
            # =====================================================

            if current is not None:

                if current["tva"] == "" and tva != "":
                    current["tva"] = tva

                if current["pu"] == "" and pu != "":
                    current["pu"] = pu

                if current["qte"] == "" and qte != "":
                    current["qte"] = qte

                if current["total"] == "" and total != "":
                    current["total"] = total

        if current is not None:

            articles.append(current)

        return articles