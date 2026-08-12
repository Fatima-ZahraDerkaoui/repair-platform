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

        text = str(text).upper().strip()

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

        # Virgule décimale
        text = text.replace(",", ".")

        # Certains OCR lisent :
        #
        # 720.00
        # 720,00
        # 720:00
        #
        # Le ":" est accepté comme séparateur décimal
        # uniquement lorsqu'il se trouve entre deux groupes
        # numériques.
        text = re.sub(
            r"(?<=\d):(?=\d{1,2}(?:\D|$))",
            ".",
            text
        )

        # Espaces multiples
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ==========================================================
    # NORMALISATION NUMERIQUE
    # ==========================================================

    def normalize_numeric(self, text):

        text = self.normalize(text)

        # Suppression des espaces dans les montants :
        #
        # 1 080,00 -> 1080.00
        # 1 080.00 -> 1080.00
        #
        text = text.replace(" ", "")

        # Suppression des unités monétaires
        text = re.sub(
            r"(DHS|MAD|DH)$",
            "",
            text
        )

        return text

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
    # SCORE POSITION NUMERIQUE
    # ==========================================================

    def score_numeric_position(self, x, column):

        if column not in self.colonnes:
            return 0

        distance = abs(
            x - self.colonnes[column]
        )

        # Une valeur numérique doit être classée
        # prioritairement selon sa colonne réelle.
        #
        # Plus la valeur est proche du centre de la colonne,
        # plus le score augmente fortement.
        #
        # Cela évite par exemple :
        #
        # 1080.00 à x=1160
        #
        # d'être classé PU uniquement parce qu'il est
        # également un prix valide.

        return max(
            0,
            240 - distance * 2
        )

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

        try:
            value = int(text)
        except (ValueError, TypeError):
            return False

        return 1 <= value <= 1000
    
    def score_quantity(self, text):

        if self.is_quantity(text):
            return 100

        # Un nombre décimal / montant n'est PAS
        # une quantité.
        return -80

    # ==========================================================
    # PRIX
    # ==========================================================

    def is_price(self, text):

        text = self.normalize_numeric(text)

        if not text:
            return False

        # Format monétaire accepté :
        #
        # 300
        # 300.00
        # 300,00
        # 720:00
        # 1 080,00
        #
        if not re.fullmatch(
            r"\d+(?:\.\d+)?",
            text
        ):
            return False

        try:
            value = float(text)
        except (ValueError, TypeError):
            return False

        # Un prix de facture doit être suffisamment élevé.
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

        # ======================================================
        # Valeur numérique
        # ======================================================

        if self.is_price(text):
            return False

        if self.is_quantity(text):
            return False

        if self.is_tva(text):
            return False

        # ======================================================
        # Mots connus
        # ======================================================

        if text in self.designation_words:
            return True

        # ======================================================
        # Désignation contenant plusieurs mots
        # ======================================================

        words = text.split()

        if len(words) >= 2:
            return True

        # ======================================================
        # Description suffisamment longue
        # ======================================================

        if len(text) >= 8:
            return True

        # ======================================================
        # Slash
        # ======================================================

        if "/" in text and len(text) >= 4:
            return True

        # ======================================================
        # Tiret
        #
        # Attention :
        # une référence peut également contenir '-'
        # ======================================================

        if "-" in text:

            # Si c'est clairement une référence,
            # ce n'est pas une désignation.
            if self.score_reference(text) >= 50:
                return False

            return len(text) >= 6

        return False

    
    def score_designation(self, text):

        return 100 if self.is_designation(text) else 0

    # ==========================================================
    # REFERENCE
    # ==========================================================

    @staticmethod
    def score_reference(text):

        text = str(text).strip().upper()

        if not text:
            return 0

        # ------------------------------------------------------
        # Une valeur numérique ne doit jamais être une référence.
        #
        # Cela couvre :
        #
        # 720
        # 720.00
        # 720,00
        # 720:00
        # 1 080,00
        # ------------------------------------------------------

        numeric_candidate = (
            text
            .replace(" ", "")
            .replace(",", ".")
        )

        numeric_candidate = re.sub(
            r"(?<=\d):(?=\d{1,2}(?:\D|$))",
            ".",
            numeric_candidate
        )

        if re.fullmatch(
            r"\d+(?:\.\d+)?",
            numeric_candidate
        ):
            return 0

        if "%" in text:
            return 0

        # ------------------------------------------------------
        # Une valeur contenant uniquement des chiffres et ":"
        # est également considérée comme numérique.
        #
        # Exemple :
        # 720:00
        # ------------------------------------------------------

        if re.fullmatch(
            r"\d+\s*:\s*\d+",
            text
        ):
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

            is_numeric_price = self.is_price(
                texte
            )

            is_quantity_value = self.is_quantity(
                texte
            )

            is_tva_value = self.is_tva(
                texte
            )

            for colonne in self.colonnes:

                # --------------------------------------------------
                # SCORE DE BASE
                # --------------------------------------------------

                if is_numeric_price and colonne in (
                    "qte",
                    "pu",
                    "total"
                ):
                    score = self.score_numeric_position(
                        centre_x,
                        colonne
                    )
                else:
                    score = self.score_position(
                        centre_x,
                        colonne
                    )

                # --------------------------------------------------
                # DESIGNATION
                # --------------------------------------------------

                if colonne == "designation":

                    score += self.score_designation(
                        texte
                    )

                # --------------------------------------------------
                # REFERENCE
                # --------------------------------------------------

                elif colonne == "reference":

                    score += self.score_reference(
                        texte
                    )

                # --------------------------------------------------
                # TVA
                # --------------------------------------------------

                elif colonne == "tva":

                    score += self.score_tva(
                        texte
                    )

                # --------------------------------------------------
                # QUANTITE
                # --------------------------------------------------

                elif colonne == "qte":

                    score += self.score_quantity(
                        texte
                    )

                # --------------------------------------------------
                # PRIX / TOTAL
                # --------------------------------------------------

                elif colonne in (
                    "pu",
                    "total"
                ):

                    score += self.score_price(
                        texte
                    )

                scores[colonne] = score

            # ======================================================
            # REGLES DE SECURITE NUMERIQUES
            # ======================================================

            if is_numeric_price:

                # Une valeur numérique valide ne doit pas devenir
                # une référence ou une désignation.

                for forbidden_column in (
                    "reference",
                    "designation"
                ):

                    if forbidden_column in scores:

                        scores[
                            forbidden_column
                        ] = -1000

                # Une valeur décimale ne doit normalement pas
                # être une quantité.

                if (
                    not is_quantity_value
                    and "qte" in scores
                ):

                    scores["qte"] -= 200

            # ======================================================
            # TVA PRIORITAIRE
            # ======================================================

            if is_tva_value and "tva" in scores:

                scores["tva"] += 300

                for column in (
                    "reference",
                    "designation",
                    "qte",
                    "pu",
                    "total"
                ):

                    if column in scores:
                        scores[column] -= 300

            # ======================================================
            # CHOIX FINAL
            # ======================================================

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

    def score_total_relationship(
        self,
        element,
        elements
    ):

        text = self.normalize_numeric(
            element.get("text", "")
        )

        if not self.is_price(text):

            return 0

        try:
            value = float(text)

        except (ValueError, TypeError):

            return 0

        x = self.get_x(element)

        qte_values = []
        pu_values = []

        for other in elements:

            if other is element:
                continue

            if other.get("column") == "qte":

                qte_text = self.normalize_numeric(
                    other.get("text", "")
                )

                if self.is_quantity(qte_text):

                    qte_values.append(
                        float(qte_text)
                    )

            elif other.get("column") == "pu":

                pu_text = self.normalize_numeric(
                    other.get("text", "")
                )

                if self.is_price(pu_text):

                    pu_values.append(
                        float(pu_text)
                    )

        if not qte_values or not pu_values:

            return 0

        for qte in qte_values:

            for pu in pu_values:

                expected = round(
                    qte * pu,
                    2
                )

                if abs(
                    expected - value
                ) <= 0.05:

                    # valeur correspondant à
                    # quantité × PU = TOTAL
                    return 180

        return 0
