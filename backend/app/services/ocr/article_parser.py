import re


class ArticleParser:

    def __init__(self):

        self.reference_pattern = re.compile(
            r"^[A-Z0-9]{2,}(?:[-_/][A-Z0-9]+)+",
            re.IGNORECASE
        )

    # =====================================================

    def normalize_text(self, text):

        if not text:
            return ""

        text = text.replace("\n", " ")

        text = text.replace("É", "E")
        text = text.replace("È", "E")
        text = text.replace("Ê", "E")
        text = text.replace("À", "A")
        text = text.replace("Ç", "C")

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # =====================================================

    def remove_duplicate_words(self, text):

        words = text.split()

        result = []

        for word in words:

            if len(result) == 0:

                result.append(word)

                continue

            if result[-1].upper() != word.upper():

                result.append(word)

        return " ".join(result)

    # =====================================================
    def clean_designation(self, designation):

        designation = self.normalize_text(designation)

        designation = self.remove_duplicate_words(designation)

        # espaces inutiles
        designation = designation.replace(" ,", ",")
        designation = designation.replace(" .", ".")

        # supprimer les caractères parasites au début
        designation = re.sub(r"^[\s\-=:;.,_]+", "", designation)

        # supprimer les espaces multiples
        designation = re.sub(r"\s{2,}", " ", designation)

        return designation.strip()

    # =====================================================

    def to_float(self, text):

        if text is None:

            return None

        text = self.normalize_text(text)

        text = text.replace("DH", "")
        text = text.replace("DHS", "")
        text = text.replace("MAD", "")
        text = text.replace("%", "")

        text = text.replace(" ", "")

        # format européen
        if "," in text and "." in text:

            if text.rfind(",") > text.rfind("."):

                text = text.replace(".", "")
                text = text.replace(",", ".")

            else:

                text = text.replace(",", "")

        else:

            text = text.replace(",", ".")

        try:

            return float(text)

        except:

            return None

    # =====================================================

    def is_valid_quantity(self, value):

        if value is None:

            return False

        return 0 < value < 10000

    # =====================================================

    def is_valid_price(self, value):

        if value is None:

            return False

        return value >= 0

    # =====================================================

    def is_valid_tva(self, value):

        if value is None:

            return False

        return 0 <= value <= 100

    # =====================================================
    def is_reference(self, text):

        if not text:
                return False

        text = self.normalize_text(text)

        text = text.replace("=", "")
        text = text.replace(":", "")
        text = text.strip()

        patterns = [

            # HP-F6V25AE
            r"^[A-Z]{2,}-[A-Z0-9]+$",

            # EPST103BK
            r"^[A-Z]{3,}[0-9]+[A-Z0-9]*$",

            # CANGI490Y
            r"^[A-Z]{4,}[0-9]+[A-Z]*$",

            # LEN-100245
            r"^[A-Z]{2,}-[0-9A-Z]+$",

            # A125-45B
            r"^[A-Z][0-9]+-[0-9A-Z]+$"

        ]

        for pattern in patterns:

            if re.match(pattern, text):

                return True

        return False

    def split_reference(self, text):

        text = self.clean_designation(text)

        if not text:

            return "", ""

        # ------------------------------------------
        # On récupère le premier mot
        # ------------------------------------------

        premier = text.split()[0]

        premier = premier.strip()

        premier = premier.replace("=", "")
        premier = premier.replace(":", "")

        # ------------------------------------------
        # Cas :
        # HP-F6V25AE-Cartouche HP
        # ------------------------------------------

        m = re.match(r"^([A-Z]{2,}-[A-Z0-9]+)-(.*)$", premier)

        if m:

            reference = m.group(1)

            reste = m.group(2)

            designation = (reste + " " + text[len(premier):]).strip()

            designation = designation.lstrip("-")

            return reference, self.clean_designation(designation)

        # ------------------------------------------
        # Cas :
        # EPST103BK-(...)
        # ------------------------------------------

        m = re.match(r"^([A-Z]{3,}[0-9]+[A-Z0-9]*)(.*)$", premier)

        if m:

            reference = m.group(1)

            reste = m.group(2)

            designation = (reste + " " + text[len(premier):]).strip()

            designation = designation.lstrip("-")

            return reference, self.clean_designation(designation)

        # ------------------------------------------
        # Cas :
        # CANGI490M-CARTOUCHE...
        # ------------------------------------------

        m = re.match(r"^([A-Z]{4,}[0-9]+[A-Z]*)(.*)$", premier)

        if m:

            reference = m.group(1)

            reste = m.group(2)

            designation = (reste + " " + text[len(premier):]).strip()

            designation = designation.lstrip("-")

            return reference, self.clean_designation(designation)

        # ------------------------------------------
        # Cas :
        # LEN-100245 Laptop
        # ------------------------------------------

        if self.is_reference(premier):

            designation = text[len(premier):].strip()

            return premier, self.clean_designation(designation)

        return "", self.clean_designation(text)

    # =====================================================

    def parse_line(self, ligne):

        article = {

            "reference": "",

            "designation": "",

            "quantite": None,

            "prix_unitaire": None,

            "tva": None,

            "total": None

        }

        designation_parts = []

        for cellule in ligne:

            colonne = cellule["column"]

            texte = self.normalize_text(cellule["text"])

            if colonne == "designation":

                designation_parts.append(texte)

            elif colonne == "qte":

                value = self.to_float(texte)

                if (
                    self.is_valid_quantity(value)
                    and article["quantite"] is None
                ):

                    article["quantite"] = int(value)

            elif colonne == "pu":

                value = self.to_float(texte)

                if (
                    self.is_valid_price(value)
                    and article["prix_unitaire"] is None
                ):

                    article["prix_unitaire"] = value

            elif colonne == "tva":

                value = self.to_float(texte)

                if (
                    self.is_valid_tva(value)
                    and article["tva"] is None
                ):

                    article["tva"] = value

            elif colonne == "total":

                value = self.to_float(texte)

                if (
                    self.is_valid_price(value)
                    and article["total"] is None
                ):

                    article["total"] = value

        designation = " ".join(designation_parts)

        designation = self.clean_designation(designation)

        ref, des = self.split_reference(designation)

        article["reference"] = ref

        article["designation"] = des

        return article

    # =====================================================

    def parse(self, lignes):

        articles = []

        for ligne in lignes:

            article = self.parse_line(ligne)

            if article["designation"]:

                articles.append(article)

        return articles
    