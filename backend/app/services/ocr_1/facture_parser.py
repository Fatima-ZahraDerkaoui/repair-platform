import re
from app.services.ocr_1.article_parser import ArticleParser

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

        for ligne in lignes:

            article = ArticleParser.parse_line(ligne)

            if article is None:
                continue

            if article["reference"] == "":
                continue

            articles.append(article)

        return articles

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