import re
from typing import Any, Dict, List, Optional


class ArticleParser:

    # ==========================================================
    # CONSTANTES DE CLASSE
    # IMPORTANT :
    # Elles doivent être ici et non dans __init__
    # ==========================================================

    HEADER_WORDS = {
        "REFERENCE",
        "RÉFÉRENCE",
        "DESIGNATION",
        "DÉSIGNATION",
        "QUANTITE",
        "QUANTITÉ",
        "QTE",
        "PU",
        "PRIX",
        "PRIX UNITAIRE",
        "EXUNITAINO",
        "MONTANT",
        "MONTANT TTC",
        "TOTAL",
        "TVA",
        "TAUX",
        "BASE",
    }

    FOOTER_WORDS = {
        "TOTALHT",
        "TOTAL HT",
        "TOTALTTC",
        "TOTAL TTC",
        "TOTALTVA",
        "TOTAL TVA",
        "BASE",
        "TAUX",
        "MONTANT",
        "ARRÊTÉE",
        "ARRETEE",
        "MODE DE REGLEMENT",
        "MODE DE RÈGLEMENT",
    }

    SUPPLIER_WORDS = {
        "SARL",
        "MAFOCOPI",
        "CASINFO",
        "ADRESSE",
        "TEL",
        "TÉL",
        "TELEPHONE",
        "TÉLÉPHONE",
        "FAX",
        "EMAIL",
        "ICE",
        "IF",
        "RC",
    }

    # Mots qui indiquent généralement une désignation
    DESCRIPTION_WORDS = {
        "TONER",
        "CARTOUCHE",
        "BOUTEILLE",
        "ENCRE",
        "TAMBOUR",
        "MINOLTA",
        "RICOH",
        "EPSON",
        "CANON",
        "HP",
        "BROTHER",
        "SAMSUNG",
        "LASER",
        "POUR",
        "BLACK",
        "CYAN",
        "MAGENTA",
        "YELLOW",
        "COULEUR",
        "COLOR",
    }

    # ==========================================================
    # INIT
    # ==========================================================

    def __init__(self):
        pass

    # ==========================================================
    # NORMALISATION
    # ==========================================================

    @staticmethod
    def normalize(text: Any) -> str:

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
            "Î": "I",
            "Ï": "I",
            "Ô": "O",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ==========================================================
    # NOMBRE
    # ==========================================================

    @staticmethod
    def parse_number(text: Any) -> Optional[float]:

        if text is None:
            return None

        text = str(text).strip()

        if not text:
            return None

        # 720:00 = faux nombre / OCR time-like
        if ":" in text:
            return None

        text = text.replace(" ", "")
        text = text.replace(",", ".")

        # OCR fréquent
        text = text.replace("O", "0")

        if not re.fullmatch(r"\d+(?:\.\d+)?", text):
            return None

        try:
            return float(text)
        except ValueError:
            return None

    # ==========================================================
    # QUANTITE
    # ==========================================================

    @classmethod
    def parse_quantity(cls, text: Any) -> Optional[int]:

        value = cls.parse_number(text)

        if value is None:
            return None

        if value <= 0:
            return None

        if value != int(value):
            return None

        value = int(value)

        if value > 1000:
            return None

        return value

    # ==========================================================
    # TEXTE
    # ==========================================================

    @classmethod
    def is_text(cls, text: Any) -> bool:

        text = cls.normalize(text)

        if not text:
            return False

        return bool(re.search(r"[A-Z]", text))

    # ==========================================================
    # FAUSSE REFERENCE
    # ==========================================================

    @classmethod
    def is_invalid_reference(cls, text: Any) -> bool:

        text = cls.normalize(text)

        if not text:
            return True

        if text in cls.HEADER_WORDS:
            return True

        if text in cls.FOOTER_WORDS:
            return True

        if text in cls.SUPPLIER_WORDS:
            return True

        # 720:00
        if ":" in text:
            return True

        # nombre seul
        if cls.parse_number(text) is not None:
            return True

        return False

    # ==========================================================
    # REFERENCE
    # ==========================================================

    @classmethod
    def clean_reference(cls, text: Any) -> Optional[str]:

        text = cls.normalize(text)

        if cls.is_invalid_reference(text):
            return None

        # Une référence doit contenir lettres + chiffres
        if not re.search(r"[A-Z]", text):
            return None

        if not re.search(r"\d", text):
            return None

        # Trop long = probablement désignation
        if len(text) > 35:
            return None

        # Mots clairement descriptifs
        for word in cls.DESCRIPTION_WORDS:

            if word in text:
                return None

        return text

    # ==========================================================
    # EXTRAIRE REFERENCE DEPUIS UNE DESIGNATION
    #
    # IMPORTANT POUR L'ANCIEN FORMAT
    #
    # Exemple :
    #
    # HP-F6V25AE Cartouche HP 652 Black
    #
    # ou
    #
    # EPST103BK Bouteille d'encre Epson...
    # ==========================================================

    @classmethod
    def extract_reference_from_text(cls, text: Any) -> Optional[str]:

        text = cls.normalize(text)

        if not text:
            return None

        # ------------------------------------------------------
        # Références avec tiret
        # HP-F6V25AE
        # HP-W2072A
        # ------------------------------------------------------

        matches = re.findall(
            r"\b[A-Z]{1,8}-[A-Z0-9]{2,20}\b",
            text
        )

        for match in matches:

            ref = cls.clean_reference(match)

            if ref:
                return ref

        # ------------------------------------------------------
        # Références alphanumériques classiques
        #
        # EPST103BK
        # CANGI490M
        # HPCH561HE
        # ------------------------------------------------------

        tokens = re.findall(
            r"\b[A-Z]{2,8}[A-Z0-9]{3,20}\b",
            text
        )

        for token in tokens:

            ref = cls.clean_reference(token)

            if ref:
                return ref

        return None

    # ==========================================================
    # DESIGNATION
    # ==========================================================

    @classmethod
    def clean_designation(cls, values: List[str]) -> Optional[str]:

        result = []

        for value in values:

            value = cls.normalize(value)

            if not value:
                continue

            if value in cls.HEADER_WORDS:
                continue

            if value in cls.FOOTER_WORDS:
                continue

            if value in cls.SUPPLIER_WORDS:
                continue

            # Nombre seul
            if cls.parse_number(value) is not None:
                continue

            # 720:00
            if ":" in value:
                continue

            # Si toute la valeur est uniquement une référence,
            # elle ne doit pas être répétée dans designation.
            ref = cls.clean_reference(value)

            if ref == value:
                continue

            result.append(value)

        if not result:
            return None

        # supprimer doublons consécutifs
        cleaned = []

        for value in result:

            if not cleaned or cleaned[-1] != value:
                cleaned.append(value)

        return " ".join(cleaned)

    # ==========================================================
    # ELEMENTS D'UNE LIGNE
    # ==========================================================

    @staticmethod
    def _elements(line):

        if line is None:
            return []

        if isinstance(line, list):
            return line

        if isinstance(line, dict):

            for key in (
                "elements",
                "items",
                "data"
            ):

                if key in line and isinstance(line[key], list):
                    return line[key]

        return []

    # ==========================================================
    # TEXTE ELEMENT
    # ==========================================================

    @staticmethod
    def _text(element):

        if not isinstance(element, dict):
            return ""

        return str(
            element.get("text", "")
        ).strip()

    # ==========================================================
    # COLONNE
    # ==========================================================

    @staticmethod
    def _column(element):

        if not isinstance(element, dict):
            return ""

        return str(
            element.get("column", "")
        ).lower().strip()

    # ==========================================================
    # X
    # ==========================================================

    @staticmethod
    def _x(element):

        try:
            return float(
                element.get("x", 0)
            )
        except Exception:
            return 0.0

    # ==========================================================
    # REFERENCE
    # ==========================================================

    def find_reference(self, elements):

        candidates = []

        for element in elements:

            text = self._text(element)
            column = self._column(element)
            x = self._x(element)

            if not text:
                continue

            # --------------------------------------------------
            # Cas 1 : vraie colonne reference
            # --------------------------------------------------

            reference = self.clean_reference(text)

            if reference:

                score = 0

                if column == "reference":
                    score += 200

                # référence généralement à gauche
                if x < 350:
                    score += 80

                if "-" in reference:
                    score += 20

                candidates.append(
                    (score, reference)
                )

        if candidates:

            candidates.sort(
                key=lambda item: item[0],
                reverse=True
            )

            return candidates[0][1]

        # ------------------------------------------------------
        # Cas 2 : ANCIEN FORMAT
        #
        # Pas de colonne reference.
        #
        # La référence peut être dans designation.
        # ------------------------------------------------------

        for element in elements:

            text = self._text(element)

            if not text:
                continue

            reference = self.extract_reference_from_text(
                text
            )

            if reference:
                return reference

        return None

    # ==========================================================
    # DESIGNATION
    # ==========================================================

    def find_designation(self, elements, reference=None):

        values = []

        for element in elements:

            text = self._text(element)
            column = self._column(element)

            if not text:
                continue

            # -----------------------------------------------
            # colonne designation
            # -----------------------------------------------

            if column == "designation":

                values.append(text)
                continue

            # -----------------------------------------------
            # ancien format
            #
            # colonne parfois mal classifiée :
            # on accepte les textes contenant une description
            # -----------------------------------------------

            if column == "":

                if self.is_text(text):

                    values.append(text)

        designation = self.clean_designation(
            values
        )

        # ------------------------------------------------------
        # Supprimer la référence si elle se trouvait au début
        # ------------------------------------------------------

        if designation and reference:

            designation = re.sub(
                rf"^\s*{re.escape(reference)}\s*",
                "",
                designation,
                flags=re.IGNORECASE
            ).strip()

        return designation

    # ==========================================================
    # QUANTITE
    # ==========================================================

    def find_quantity(self, elements):

        candidates = []

        for element in elements:

            text = element.get("text", "")
            column = element.get("column")
            x = element.get("x", 0)

            # -------------------------------------------------
            # Une quantité explicite doit venir de la colonne
            # qte.
            # -------------------------------------------------
            if column != "qte":
                continue

            text = str(text).strip()

            # -------------------------------------------------
            # Une quantité doit être un entier simple.
            # Exemple : 2, 3, 6
            # -------------------------------------------------
            if not re.fullmatch(r"\d+", text):
                continue

            try:
                value = int(text)
            except ValueError:
                continue

            # -------------------------------------------------
            # Évite les valeurs absurdes
            # -------------------------------------------------
            if not (1 <= value <= 100):
                continue

            candidates.append({
                "value": value,
                "x": x
            })

        # -----------------------------------------------------
        # Aucun QTE détecté
        # → le parse_line() fera ensuite :
        #
        # QTE = TOTAL / PU
        # -----------------------------------------------------
        if not candidates:
            return None

        # -----------------------------------------------------
        # S'il y en a plusieurs, prendre celui le plus proche
        # de la colonne QTE.
        # -----------------------------------------------------
        if hasattr(self, "colonnes") and self.colonnes:
            qte_x = self.colonnes.get("qte")

            if qte_x is not None:
                candidates.sort(
                    key=lambda e: abs(e["x"] - qte_x)
                )
                return candidates[0]["value"]

        return candidates[0]["value"]

    # ==========================================================
    # PRIX UNITAIRE
    # ==========================================================

    def find_unit_price(self, elements):

        candidates = []

        for element in elements:

            text = element.get("text", "")
            column = element.get("column")
            x = element.get("x", 0)

            value = self.clean_number(text)

            if value is None:
                continue

            if column not in ("pu", "total"):
                continue

            candidates.append({
                "value": value,
                "x": x
            })

        if not candidates:
            return None

        candidates.sort(key=lambda e: e["x"])

        # -------------------------------------------------
        # Le montant le plus à droite = TOTAL
        # Le précédent = PU
        # -------------------------------------------------

        if len(candidates) >= 2:
            return candidates[-2]["value"]

        return None

    # ==========================================================
    # TOUS LES NOMBRES
    # ==========================================================

    def numeric_elements(self, elements):

        result = []

        for element in elements:

            text = self._text(element)

            value = self.parse_number(text)

            if value is None:
                continue

            result.append({
                "value": value,
                "text": text,
                "column": self._column(element),
                "x": self._x(element),
            })

        return result

    # ==========================================================
    # TOTAL
    # ==========================================================

    def find_total(self, elements):

        candidates = []

        for element in elements:

            text = element.get("text", "")
            column = element.get("column")
            x = element.get("x", 0)

            value = self.clean_number(text)

            if value is None:
                continue

            if column not in ("pu", "total"):
                continue

            candidates.append({
                "value": value,
                "x": x
            })

        if not candidates:
            return None

        candidates.sort(key=lambda e: e["x"])

        return candidates[-1]["value"]

    # ==========================================================
    # CALCUL PU
    # ==========================================================

    @staticmethod
    def calculate_unit_price(
        quantity,
        total
    ):

        if quantity is None or total is None:
            return None

        if quantity <= 0:
            return None

        return round(
            total / quantity,
            2
        )

    # ==========================================================
    # CALCUL QUANTITE
    # ==========================================================

    @staticmethod
    def calculate_quantity(
        unit_price,
        total
    ):

        if unit_price is None or total is None:
            return None

        if unit_price <= 0:
            return None

        q = total / unit_price

        if abs(
            q - round(q)
        ) < 0.01:

            q = int(round(q))

            if 1 <= q <= 100:
                return q

        return None

    # ==========================================================
    # CALCUL TOTAL
    # ==========================================================

    @staticmethod
    def calculate_total(
        quantity,
        unit_price
    ):

        if quantity is None or unit_price is None:
            return None

        return round(
            quantity * unit_price,
            2
        )

    # ==========================================================
    # TVA
    # ==========================================================

    def find_tva(self, elements):

        for element in elements:

            text = self._text(element)
            column = self._column(element)

            normalized = self.normalize(text)

            # 20%
            match = re.fullmatch(
                r"(\d+(?:\.\d+)?)%",
                normalized
            )

            if match:

                return float(
                    match.group(1)
                )

            # colonne TVA
            if column == "tva":

                value = self.parse_number(text)

                if value is not None:

                    if 0 < value <= 100:
                        return value

        return None

    # ==========================================================
    # PARSE UNE LIGNE
    # ==========================================================
    def parse_line(self, elements):

        reference = self.find_reference(elements)

        designation = self.find_designation(elements)

        # QTE OCR
        quantity = self.find_quantity(elements)

        # PU
        prix_unitaire = self.find_unit_price(elements)

        # TOTAL
        total = self.find_total(elements)

        # TVA
        tva = self.find_tva(elements)

        # Si QTE absente → TOTAL / PU
        quantity = self.infer_quantity(
            prix_unitaire,
            total,
            quantity
        )

        return {
            "reference": reference,
            "designation": designation,
            "quantite": quantity,
            "prix_unitaire": prix_unitaire,
            "tva": tva,
            "total": total
        }

    # ==========================================================
    # PARSE GLOBAL
    # ==========================================================

    def parse(self, lignes):

        articles = []

        if not lignes:
            return articles

        for line in lignes:

            article = self.parse_line(
                line
            )

            if article is None:
                continue

            if not article.get("reference"):
                continue

            articles.append(
                article
            )

        return articles

    def infer_quantity(self, prix_unitaire, total, quantity=None):

        # Quantité déjà détectée par OCR
        if quantity is not None:
            try:
                q = int(quantity)

                if q > 0:
                    return q

            except (ValueError, TypeError):
                pass

        # Impossible de calculer
        if prix_unitaire is None or total is None:
            return None

        try:
            pu = float(prix_unitaire)
            montant = float(total)

        except (ValueError, TypeError):
            return None

        if pu <= 0 or montant <= 0:
            return None

        # Déduction :
        # quantité = total / prix unitaire

        q = montant / pu
        q_round = round(q)

        # La quantité doit être entière
        if q_round <= 0:
            return None

        # Tolérance
        if abs(q - q_round) <= 0.01:
            return q_round

        return None

    def clean_number(self, text):

        if text is None:
            return None

        text = str(text).strip()

        # OCR : 720:00 → 720.00
        text = text.replace(":", ".")

        # virgule française
        text = text.replace(",", ".")

        # espaces
        text = text.replace(" ", "")

        # garder uniquement les nombres
        if not re.fullmatch(r"\d+(?:\.\d+)?", text):
            return None

        try:
            return float(text)
        except ValueError:
            return None