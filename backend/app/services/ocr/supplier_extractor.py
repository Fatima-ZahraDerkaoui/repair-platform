import re


class SupplierExtractor:

    def __init__(self):
        pass

    # ==========================================================
    # Normalisation
    # ==========================================================

    @staticmethod
    def normalize(text):

        text = text.upper()

        replacements = {

            "É": "E",
            "È": "E",
            "Ê": "E",
            "Ë": "E",

            "À": "A",
            "Â": "A",

            "Ù": "U",
            "Û": "U",

            "Ô": "O",
            "Ö": "O",

            "Î": "I",
            "Ï": "I",

            "Ç": "C"

        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ==========================================================
    # Nom fournisseur
    # ==========================================================

    def extract_name(self, texte):

        lignes = texte.splitlines()

        lignes = [l.strip() for l in lignes if l.strip()]

        blacklist = [

            "FACTURE",
            "BL",
            "BON DE LIVRAISON",
            "DEVIS",
            "DATE",
            "TOTAL",
            "TVA",
            "TEL",
            "FAX",
            "EMAIL",
            "ICE",
            "IF",
            "RC",
            "PATENTE",
            "CNSS",
            "RIB",
            "CLIENT",
            "DESIGNATION",
            "REFERENCE"

        ]

        for ligne in lignes[:20]:

            original = ligne.strip()

            upper = self.normalize(original)

            if len(original) < 3:
                continue

            if any(word in upper for word in blacklist):
                continue

            if re.search(r"\d{4,}", upper):
                continue

            return original

        return None

    # ==========================================================
    # Téléphone
    # ==========================================================
    def extract_phone(self, texte):

        texte = texte.replace("\n", " ")

        pattern = r"(?:\+212|0)\s*[5-7](?:[\s.\-/]?\d{2}){4}"

        numeros = re.findall(pattern, texte)

        resultat = []

        for numero in numeros:

            numero = re.sub(r"[^\d+]", "", numero)

            if numero not in resultat:
                resultat.append(numero)

        return resultat

    # ==========================================================
    # Email
    # ==========================================================

    def extract_email(self, texte):
        return None

    # ==========================================================
    # Fax
    # ==========================================================

    def extract_fax(self, texte):
        return None

    # ==========================================================
    # Adresse
    # ==========================================================

    def extract_address(self, texte):
        return None

    # ==========================================================
    # Ville
    # ==========================================================

    def extract_city(self, texte):
        return None

    # ==========================================================
    # Pays
    # ==========================================================

    def extract_country(self, texte):
        return None

    # ==========================================================
    # ICE
    # ==========================================================

    def extract_ice(self, texte):
        return None

    # ==========================================================
    # IF
    # ==========================================================

    def extract_if(self, texte):
        return None

    # ==========================================================
    # RC
    # ==========================================================

    def extract_rc(self, texte):
        return None

    # ==========================================================
    # Patente
    # ==========================================================

    def extract_patente(self, texte):
        return None

    # ==========================================================
    # CNSS
    # ==========================================================

    def extract_cnss(self, texte):
        return None

    # ==========================================================
    # RIB
    # ==========================================================

    def extract_rib(self, texte):
        return None

    # ==========================================================
    # Site Web
    # ==========================================================

    def extract_website(self, texte):
        return None

    # ==========================================================
    # Extraction complète
    # ==========================================================

    def extract(self, texte):
        

        return {

            "name": self.extract_name(texte),

            "address": self.extract_address(texte),

            "city": self.extract_city(texte),

            "country": self.extract_country(texte),

            "phone": self.extract_phone(texte),

            "fax": self.extract_fax(texte),

            "email": self.extract_email(texte),

            "website": self.extract_website(texte),

            "ice": self.extract_ice(texte),

            "if": self.extract_if(texte),

            "rc": self.extract_rc(texte),

            "patente": self.extract_patente(texte),

            "cnss": self.extract_cnss(texte),

            "rib": self.extract_rib(texte)

        }      

    
