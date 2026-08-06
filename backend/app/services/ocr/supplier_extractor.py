import re


class SupplierExtractor:

    def __init__(self):
        pass


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

    def extract_phone(self, texte):

        texte = texte.replace("\n", " ")

        pattern = r"(?:\+212|0)\s*[5-7](?:[\s.\-/]?\d{2}){4}"

        numeros = re.findall(pattern, texte)

        resultat = []

        for numero in numeros:

            numero = re.sub(r"[^\d+]", "", numero)

            if len(numero) > 10:
                continue

            if numero not in resultat:
                resultat.append(numero)

        return resultat

    def extract_email(self, texte):

        texte = texte.replace("\n", " ")

        # supprimer un éventuel RIB collé devant l'email
        texte = re.sub(
            r"\d{15,30}-(?=[A-Za-z0-9._%+-]+@)",
            "",
            texte
        )

        pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

        m = re.search(pattern, texte)

        if m:
            return m.group()

        return None

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

    def extract_website(self, texte):

        texte = texte.replace("\n", " ")

        pattern = r"(?:www\.)?[a-zA-Z0-9-]+\.(?:com|ma|fr|net|org)"

        sites = re.findall(pattern, texte)

        if sites:

            for site in sites:

                if "P.U" in site.upper():
                    continue

                return site

        return None

    def extract_fax(self, texte):

        pattern = r"FAX\s*[:.]?\s*((?:\+212|0)\s*[5-7](?:[\s.\-/]?\d{2}){4})"

        m = re.search(pattern, texte, re.IGNORECASE)

        if m:

            numero = re.sub(r"[^\d+]", "", m.group(1))

            return numero

        return None

    def extract_ice(self, texte):

        texte = self.normalize(texte)

        patterns = [

            r"(?:ICE|1CE)\s*[:.]?\s*([0-9]{10,20})",

            r"([0-9]{15,20})"

        ]

        for p in patterns:

            m = re.search(p, texte)

            if m:

                return m.group(1)

        return None

    def extract_if(self, texte):
        texte = self.normalize(texte)

        patterns = [

            r"I\.?F\.?[,:\- ]*([0-9]{5,15})",

            r"\bIF\b[,:\- ]*([0-9]{5,15})"

        ]

        for p in patterns:

            m = re.search(p, texte)

            if m:

                return m.group(1)

        return None

    def extract_rc(self, texte):

        texte = self.normalize(texte)

        patterns = [

            r"R\.?C\.?[,:\- ]*([0-9]{3,15})",

            r"RC[,:\- ]*([0-9]{3,15})"

        ]

        for p in patterns:

            m = re.search(p, texte)

            if m:

                return m.group(1)

        return None

    def extract_patente(self, texte):

        pattern = r"PATENTE\s*[:.]?\s*([0-9]{4,20})"

        m = re.search(pattern, texte, re.IGNORECASE)

        if m:
            return m.group(1)

        return None

    def extract_cnss(self, texte):

        texte = self.normalize(texte)

        patterns = [

            r"C\.?N\.?S\.?S\.?[:.]?([0-9]{4,15})",

            r"CNSS[:.]?([0-9]{4,15})"

        ]

        for p in patterns:

            m = re.search(p, texte)

            if m:

                return m.group(1)

        return None

    def extract_rib(self, texte):

        patterns = [

            r"\bRIB\b\s*[:.]?\s*([0-9 ]{10,40})",

            r"\bIBAN\b\s*[:.]?\s*([A-Z0-9 ]{15,40})"

        ]

        for pattern in patterns:

            m = re.search(pattern, texte, re.IGNORECASE)

            if m:

                rib = m.group(1)

                rib = rib.replace(" ", "")

                return rib

        return None

    def extract_city(self, texte):

        villes = [

            "CASABLANCA",
            "RABAT",
            "MARRAKECH",
            "FES",
            "MEKNES",
            "AGADIR",
            "TANGER",
            "BENI MELLAL",
            "BENIMELLAL",
            "OUJDA",
            "KENITRA",
            "SAFI",
            "EL JADIDA",
            "TEMARA"

        ]

        upper = self.normalize(texte)

        for ville in villes:

            if ville in upper:

                return ville.title()

        return None

    def extract_country(self, texte):

        upper = self.normalize(texte)

        if "MAROC" in upper:
            return "Maroc"

        if "MOROCCO" in upper:
            return "Morocco"

        return None


    def extract_address(self, texte):

        lignes = [
            l.strip()
            for l in texte.splitlines()
            if l.strip()
        ]

        # =====================================================
        # 1) Cas le plus fiable :
        # SIÈGE SOCIAL
        # =====================================================

        patterns = [

            r"SI[EÈ]GE\s+SOCIAL\s*[:\-]?\s*(.+)",

            r"SI[EÈ]GE\s*[:\-]?\s*(.+)",

            r"ADRESSE\s*[:\-]?\s*(.+)"

        ]

        for ligne in lignes:

            for pattern in patterns:

                m = re.search(pattern, ligne, re.IGNORECASE)

                if m:

                    adresse = m.group(1).strip()

                    # supprimer le nom de société devant l'adresse
                    adresse = re.sub(
                        r"^[A-Z0-9&\-\s]+[,:\-]+",
                        "",
                        adresse
                    )

                    return adresse

        # =====================================================
        # 2) Recherche d'une ligne contenant BD, Avenue...
        # =====================================================

        keywords = [

            "BD",
            "BOULEVARD",
            "AVENUE",
            "RUE",
            "LOT",
            "ZONE",
            "PARC",
            "IMMEUBLE",
            "IMM",
            "RESIDENCE",
            "RESIDENCE",
            "CENTRE"

        ]

        blacklist = [

            "CLIENT",
            "DESTINATAIRE",
            "FACTURE",
            "BL/FACTURE",
            "DATE",
            "DESIGNATION",
            "TVA",
            "TOTAL",
            "TEL",
            "FAX",
            "EMAIL",
            "ICE",
            "CNSS",
            "PATENTE",
            "RIB"

        ]

        for ligne in lignes:

            upper = self.normalize(ligne)

            if any(x in upper for x in blacklist):
                continue

            if any(k in upper for k in keywords):

                return ligne

        # =====================================================
        # 3) Dernier recours :
        # ligne contenant une ville + numéro
        # =====================================================

        villes = [

            "CASABLANCA",
            "RABAT",
            "FES",
            "MARRAKECH",
            "AGADIR",
            "TANGER",
            "MEKNES",
            "BENI",
            "BENIMELLAL"

        ]

        for ligne in lignes:

            upper = self.normalize(ligne)

            if any(v in upper for v in villes):

                if re.search(r"\d", ligne):

                    return ligne

        return None
    