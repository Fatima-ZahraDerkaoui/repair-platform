import re


class FactureParser:

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _to_float(value: str):

        if value is None:
            return None

        value = value.replace(" ", "")
        value = value.replace(",", ".")

        try:
            return float(value)
        except:
            return None

    @classmethod
    def extract_articles(cls, lignes):

        articles = []

        started = False

        for ligne in lignes:

            textes = [

                c["text"]

                for c in ligne

            ]

            ligne_txt = " ".join(textes)

            upper = ligne_txt.upper()

            if "DÉSIGNATION" in upper or "DESIGNATION" in upper:

                started = True

                continue

            if not started:
                continue

            if "TOTAL HT" in upper:
                break

            if len(textes) < 5:
                continue

            reference = textes[0]

            designation = ""

            tva = ""

            prix = None

            quantite = None

            total = None

            for t in textes[1:]:

                if "%" in t:

                    tva = t

                    continue

                if prix is None:

                    p = cls._to_float(t)

                    if p is not None:

                        prix = p

                        continue

                if quantite is None:

                    if t.isdigit():

                        quantite = int(t)

                        continue

                if total is None:

                    tt = cls._to_float(t)

                    if tt is not None:

                        total = tt

                        continue

                designation += " " + t

            articles.append({

                "reference": reference,

                "designation": designation.strip(),

                "tva": tva,

                "prix_unitaire": prix,

                "quantite": quantite,

                "total": total

            })

        return articles
    @classmethod
    def parse_article_line(cls, ligne):

        ligne = re.sub(r"\s+", " ", ligne).strip()

        tokens = ligne.split()

        if len(tokens) < 6:
            return None

        # ------------------------------------
        # Les 4 derniers nombres
        # Prix HT
        # TVA
        # Qté
        # Total
        # ------------------------------------

        numbers = []

        for token in reversed(tokens):

            if re.match(r"^[0-9]+([,.][0-9]+)?$", token):

                numbers.append(token)

            if len(numbers) == 4:
                break

        if len(numbers) != 4:
            return None

        numbers.reverse()

        prix = cls._to_float(numbers[0])

        tva = numbers[1]

        quantite = int(float(numbers[2]))

        total = cls._to_float(numbers[3])

        # ------------------------------------
        # référence
        # ------------------------------------

        reference = tokens[0]

        # ------------------------------------
        # designation
        # ------------------------------------

        designation_tokens = tokens[1:-4]

        designation = " ".join(designation_tokens)

        return {

            "reference": reference,

            "designation": designation,

            "quantite": quantite,

            "prix_unitaire": prix,

            "tva": tva,

            "total": total

        }
    
    @classmethod
    def parse(cls, texte, lignes ):

        texte_original = texte
        texte = cls._clean(texte)

        resultat = {
            "numero": None,
            "date": None,
            "fournisseur": None,
            "total_ht": None,
            "tva": None,
            "total_ttc": None,
            "articles": []
        }

        # ==================================================
        # FOURNISSEUR
        # ==================================================

        if "CASINFO" in texte.upper():
            resultat["fournisseur"] = "CASINFO"

        # ==================================================
        # NUMERO FACTURE
        # ==================================================

        numero = re.search(
            r"FV\d{4}-\d+",
            texte,
            re.IGNORECASE
        )

        if numero:
            resultat["numero"] = numero.group()

        # ==================================================
        # DATE
        # ==================================================

        date = re.search(
            r"\d{2}/\d{2}/\d{4}",
            texte
        )

        if date:
            resultat["date"] = date.group()

        # ==================================================
        # TOTAL HT + TVA + TTC
        # ==================================================
        lignes_texte = texte_original.splitlines()

        for i, ligne in enumerate(lignes_texte):

            upper = ligne.upper()

            if "TOTAL HT" in upper:

                nombres = re.findall(r"[0-9\s]+[,.][0-9]{2}", ligne)

                if nombres:
                    resultat["total_ht"] = cls._to_float(nombres[-1])
                elif i + 1 < len(lignes_texte):
                    resultat["total_ht"] = cls._to_float(lignes_texte[i + 1])

            elif "TOTAL TVA" in upper:

                nombres = re.findall(r"[0-9\s]+[,.][0-9]{2}", ligne)

                if nombres:
                    resultat["tva"] = cls._to_float(nombres[-1])
                elif i + 1 < len(lignes_texte):
                    resultat["tva"] = cls._to_float(lignes_texte[i + 1])

            elif "TOTAL TTC" in upper:

                nombres = re.findall(r"[0-9\s]+[,.][0-9]{2}", ligne)

                if nombres:
                    resultat["total_ttc"] = cls._to_float(nombres[-1])
                elif i + 1 < len(lignes_texte):
                    resultat["total_ttc"] = cls._to_float(lignes_texte[i + 1])
                    
        # ==================================================
        # EXTRACTION DES ARTICLES
        # ==================================================

        resultat["articles"] = cls.extract_articles(
            lignes
        )

        return resultat