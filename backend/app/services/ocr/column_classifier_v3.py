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
            "SAMSUNG",
            "MINOLTA",
            "RICOH",
            "TAMBOUR"
        }

    # =====================================================
    # NORMALISATION
    # =====================================================

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
            "Î": "I",
            "Ï": "I",
            "Ô": "O"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = text.replace(",", ".")

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # =====================================================
    # POSITION
    # =====================================================

    def score_position(self, x, column):

        if column not in self.colonnes:
            return 0

        distance = abs(x - self.colonnes[column])

        # On conserve une influence de la position
        score = max(0, 100 - distance)

        return score

    # =====================================================
    # TVA
    # =====================================================

    def is_tva(self, text):

        text = self.normalize(text)

        return re.fullmatch(
            r"\d+(?:\.\d+)?\s*%",
            text
        ) is not None

    def score_tva(self, text):

        return 100 if self.is_tva(text) else 0

    # =====================================================
    # QUANTITE
    # =====================================================

    def is_quantity(self, text):

        text = self.normalize(text)

        if not re.fullmatch(r"\d+", text):
            return False

        value = int(text)

        return 1 <= value <= 100

    def score_quantity(self, text):

        return 100 if self.is_quantity(text) else 0

    # =====================================================
    # PRIX
    # =====================================================

    def is_price(self, text):

        text = self.normalize(text)

        text = text.replace(" ", "")

        if not re.fullmatch(
            r"\d+(?:\.\d+)?",
            text
        ):
            return False

        try:
            value = float(text)
        except ValueError:
            return False

        # Un simple 2, 3, 6... ne doit pas devenir un prix
        if value < 10:
            return False

        return True

    def score_price(self, text):

        return 100 if self.is_price(text) else 0

    # =====================================================
    # REFERENCE
    # =====================================================

    def is_reference(self, text):

        text = self.normalize(text)

        if not text:
            return False

        # ---------------------------------------------
        # Trop long = probablement désignation
        # ---------------------------------------------

        if len(text) > 30:
            return False

        # ---------------------------------------------
        # Prix
        # ---------------------------------------------

        if re.fullmatch(
            r"\d+(?:\.\d+)?",
            text.replace(" ", "")
        ):
            return False

        # ---------------------------------------------
        # Pourcentage
        # ---------------------------------------------

        if "%" in text:
            return False

        # ---------------------------------------------
        # Minimum caractères
        # ---------------------------------------------

        if len(text) < 4:
            return False

        # ---------------------------------------------
        # Une référence contient généralement
        # lettres + chiffres
        # ---------------------------------------------

        has_letter = bool(re.search(r"[A-Z]", text))
        has_digit = bool(re.search(r"\d", text))

        if not (has_letter and has_digit):
            return False

        # ---------------------------------------------
        # Format propre de référence
        #
        # Exemples :
        # HP-F6V25AE
        # EPST103BK
        # CANGI490M
        # TATN324N
        # TTN324C
        # TATN321CWT
        # TATN3210
        # CYAF1515
        # ---------------------------------------------

        if re.fullmatch(
            r"[A-Z0-9]+(?:[-_/][A-Z0-9]+)*",
            text
        ):
            return True

        return False

    def score_reference(self, text):

        if self.is_reference(text):
            return 150

        return 0

    # =====================================================
    # DESIGNATION
    # =====================================================

    def is_designation(self, text):

        text = self.normalize(text)

        if not text:
            return False

        # Une référence doit être prioritaire
        if self.is_reference(text):
            return False

        if text in self.designation_words:
            return True

        # Texte contenant plusieurs mots
        if len(text.split()) >= 2:
            return True

        if "/" in text:
            return True

        if len(text) > 15:
            return True

        if re.search(r"[A-Z]", text):
            return True

        return False

    def score_designation(self, text):

        return 100 if self.is_designation(text) else 0

    # =====================================================
    # SCORE GENERAL REFERENCE
    # =====================================================

    @staticmethod
    def score(text):

        text = text.strip().upper()

        if not text:
            return 0

        # ---------------------------------------------
        # Prix
        # ---------------------------------------------

        if re.fullmatch(
            r"\d+(?:[.,]\d+)?",
            text.replace(" ", "")
        ):
            return 0

        # ---------------------------------------------
        # Pourcentage
        # ---------------------------------------------

        if "%" in text:
            return 0

        score = 0

        # lettres + chiffres
        if (
            re.search(r"[A-Z]", text)
            and re.search(r"\d", text)
        ):
            score += 35

        # caractères de référence
        if "-" in text or "_" in text or "/" in text:
            score += 20

        # format propre
        if re.fullmatch(
            r"[A-Z0-9\-_/\.]+",
            text
        ):
            score += 20

        # commence par lettres
        if re.match(
            r"^[A-Z]{2,}",
            text
        ):
            score += 15

        # longueur normale
        if 5 <= len(text) <= 30:
            score += 10

        return min(score, 100)

    # =====================================================
    # CLASSIFICATION FINALE
    # =====================================================

    def classify(self, elements):

        resultat = []

        for element in elements:

            x1, y1, x2, y2 = element["box"]

            centre_x = (x1 + x2) / 2
            centre_y = (y1 + y2) / 2

            texte = element["text"]

            scores = {}

            for colonne in self.colonnes:

                score = self.score_position(
                    centre_x,
                    colonne
                )

                # -----------------------------------------
                # REFERENCE
                # -----------------------------------------

                if colonne == "reference":

                    score += self.score_reference(texte)

                # -----------------------------------------
                # DESIGNATION
                # -----------------------------------------

                elif colonne == "designation":

                    score += self.score_designation(texte)

                # -----------------------------------------
                # TVA
                # -----------------------------------------

                elif colonne == "tva":

                    score += self.score_tva(texte)

                # -----------------------------------------
                # QUANTITE
                # -----------------------------------------

                elif colonne == "qte":

                    score += self.score_quantity(texte)

                # -----------------------------------------
                # PRIX
                # -----------------------------------------

                elif colonne in ("pu", "total"):

                    score += self.score_price(texte)

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
    