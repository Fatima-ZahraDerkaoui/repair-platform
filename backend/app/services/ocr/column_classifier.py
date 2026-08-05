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
   
    def normalize(self, text):

        if text is None:
            return ""

        text = text.upper()

        text = text.replace("É", "E")
        text = text.replace("È", "E")
        text = text.replace("Ê", "E")
        text = text.replace("À", "A")
        text = text.replace("Ç", "C")

        text = text.replace(",", ".")

        text = re.sub(r"\s+", " ", text)

        return text.strip()
    
    
    def score_position(self, x):

        scores = {}

        for colonne, position in self.colonnes.items():

            distance = abs(x - position)

            score = max(0, 100 - distance)

            scores[colonne] = score

        return scores

   
    def is_tva(self, text):

        text = self.normalize(text)

        return re.fullmatch(r"\d+(\.\d+)?\s*%", text) is not None


    def score_tva(self, text):

        if self.is_tva(text):
            return 100

        return 0


    def is_quantity(self, text):

        text = self.normalize(text)

        if not re.fullmatch(r"\d+", text):
            return False

        value = int(text)

        return 1 <= value <= 100

    def score_quantity(self, text):

        if self.is_quantity(text):
            return 100

        return 0

    def is_price(self, text):

        text = self.normalize(text)

        text = text.replace(" ", "")

        if not re.fullmatch(r"\d+(?:\.\d+)?", text):
            return False

        value = float(text)

        # évite que 2 ou 8 deviennent des prix
        if value < 10:
            return False

        return True

    def score_price(self, text):

        if self.is_price(text):
            return 100

        return 0
 
    def score_position(self, x, column):

        if column not in self.colonnes:
            return 0

        distance = abs(x - self.colonnes[column])

        # décroissance linéaire
        score = max(0, 100 - distance)

        return score

    @staticmethod
    def score(text):

        text = text.strip().upper()

        if not text:
            return 0

        score = 0

        # ==========================================
        # Rejeter immédiatement les prix
        # ==========================================

        if re.fullmatch(r"\d+(?:[.,]\d+)?", text.replace(" ", "")):
            return 0

        # ==========================================
        # Rejeter les pourcentages
        # ==========================================

        if "%" in text:
            return 0

        # ==========================================
        # Lettres + chiffres
        # ==========================================

        if re.search(r"[A-Z]", text) and re.search(r"\d", text):
            score += 35

        # ==========================================
        # Caractères typiques d'une référence
        # ==========================================

        if "-" in text or "_" in text or "/" in text:
            score += 20

        # ==========================================
        # Format composé uniquement de caractères autorisés
        # ==========================================

        if re.fullmatch(r"[A-Z0-9\-_/\.]+", text):
            score += 20

        # ==========================================
        # Commence par des lettres
        # ==========================================

        if re.match(r"^[A-Z]{2,}", text):
            score += 15

        # ==========================================
        # Taille normale
        # ==========================================

        if 5 <= len(text) <= 30:
            score += 10

        return min(score, 100)

        # =====================================================
    # Classification finale
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

                score = self.score_position(centre_x, colonne)

                if colonne == "designation":
                    score += self.score_designation(texte)

                elif colonne == "tva":
                    score += self.score_tva(texte)

                elif colonne == "qte":
                    score += self.score_quantity(texte)

                elif colonne in ("pu", "total"):
                    score += self.score_price(texte)

                scores[colonne] = score

            meilleure_colonne = max(scores, key=scores.get)

            resultat.append({

                "text": texte,

                "box": element["box"],

                "x": centre_x,

                "y": centre_y,

                "column": meilleure_colonne

            })

        return resultat

    def is_designation(self, text):

        text = self.normalize(text)

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

        if self.is_designation(text):
            return 100

        return 0
