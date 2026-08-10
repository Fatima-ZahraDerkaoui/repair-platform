import re


class ColumnClassifier:

    def __init__(self, colonnes):

        self.colonnes = colonnes

        self.colors = {
            "BLACK",
            "CYAN",
            "MAGENTA",
            "YELLOW",
            "COLOR",
            "COULEUR"
        }

        self.designation_words = {
            "POUR",
            "BLACK",
            "CYAN",
            "MAGENTA",
            "YELLOW",
            "COULEUR",
            "COLOR",
            "LASER",
            "TONER",
            "CARTOUCHE",
            "ENCRE",
            "BOUTEILLE",
            "EPSON",
            "CANON",
            "HP",
            "BROTHER",
            "SAMSUNG"
        }

    # ==========================================================
    # NORMALISATION
    # ==========================================================

    def normalize(self, text):

        if text is None:
            return ""

        text = str(text).upper()

        replacements = {
            "É": "E",
            "È": "E",
            "Ê": "E",
            "Ë": "E",
            "À": "A",
            "Â": "A",
            "Ç": "C",
            "Ù": "U",
            "Û": "U",
            "Ô": "O",
            "Ö": "O",
            "Î": "I",
            "Ï": "I",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = text.replace(",", ".")

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ==========================================================
    # POSITION
    # ==========================================================

    def score_position(self, x, column):

        if column not in self.colonnes:
            return 0

        distance = abs(
            x - self.colonnes[column]
        )

        # Très forte importance de la position.
        score = max(
            0,
            160 - distance
        )

        return score

    # ==========================================================
    # TVA
    # ==========================================================

    def is_tva(self, text):

        text = self.normalize(text)

        return (
            re.fullmatch(
                r"\d+(?:\.\d+)?\s*%",
                text
            )
            is not None
        )

    def score_tva(self, text):

        return 140 if self.is_tva(text) else 0

    # ==========================================================
    # QUANTITE
    # ==========================================================

    def is_quantity(self, text):

        text = self.normalize(text)

        if not re.fullmatch(
            r"\d+",
            text
        ):
            return False

        value = int(text)

        return 1 <= value <= 100

    def score_quantity(self, text):

        if self.is_quantity(text):
            return 100

        # Un nombre décimal / montant n'est PAS une quantité.
        return -80

    # ==========================================================
    # PRIX
    # ==========================================================

    def is_price(self, text):

        text = self.normalize(text)

        text = text.replace(" ", "")

        if not re.fullmatch(
            r"\d+(?:\.\d+)?",
            text
        ):
            return False

        value = float(text)

        if value < 10:
            return False

        return True

    def score_price(self, text):

        return 100 if self.is_price(text) else 0

    # ==========================================================
    # DESIGNATION
    # ==========================================================

    def is_designation(self, text):

        text = self.normalize(text)

        if not text:
            return False

        if text in self.designation_words:
            return True

        if "/" in text:
            return True

        if "-" in text:
            return True

        if len(text) > 15:
            return True

        if re.search(r"[A-Z]", text):
            return True

        return False

    def score_designation(self, text):

        return 100 if self.is_designation(text) else 0

    # ==========================================================
    # REFERENCE
    # ==========================================================

    @staticmethod
    def score_reference(text):

        text = text.strip().upper()

        if not text:
            return 0

        if re.fullmatch(
            r"\d+(?:[.,]\d+)?",
            text.replace(" ", "")
        ):
            return 0

        if "%" in text:
            return 0

        score = 0

        if (
            re.search(r"[A-Z]", text)
            and re.search(r"\d", text)
        ):
            score += 35

        if "-" in text or "_" in text or "/" in text:
            score += 20

        if re.fullmatch(
            r"[A-Z0-9\-_/\.]+",
            text
        ):
            score += 20

        if re.match(
            r"^[A-Z]{2,}",
            text
        ):
            score += 15

        if 5 <= len(text) <= 30:
            score += 10

        return min(score, 100)

    # ==========================================================
    # CLASSIFICATION
    # ==========================================================

    def classify(self, elements):

        resultat = []

        for element in elements:

            x1, y1, x2, y2 = element["box"]

            centre_x = (
                x1 + x2
            ) / 2

            centre_y = (
                y1 + y2
            ) / 2

            texte = element.get(
                "text",
                ""
            )

            scores = {}

            for colonne in self.colonnes:

                score = self.score_position(
                    centre_x,
                    colonne
                )

                if colonne == "designation":

                    score += self.score_designation(
                        texte
                    )

                elif colonne == "reference":

                    score += self.score_reference(
                        texte
                    )

                elif colonne == "tva":

                    score += self.score_tva(
                        texte
                    )

                elif colonne == "qte":

                    score += self.score_quantity(
                        texte
                    )

                elif colonne in (
                    "pu",
                    "total"
                ):

                    score += self.score_price(
                        texte
                    )

                scores[colonne] = score

            meilleure_colonne = max(
                scores,
                key=scores.get
            )

            resultat.append({

                "text": texte,

                "box": element["box"],

                "x": centre_x,

                "y": centre_y,

                "column": meilleure_colonne

            })

        return resultat
    