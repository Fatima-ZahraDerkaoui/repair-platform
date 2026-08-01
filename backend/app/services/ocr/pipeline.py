from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.document_classifier import DocumentClassifier
from app.services.ocr.facture_parser import FactureParser
from app.services.ocr.table_builder import TableBuilder
from app.services.ocr.article_parser import ArticleParser
from app.services.ocr.table_merger import TableMerger

class OCRPipeline:

    def __init__(self):

        self.engine = OCREngine()

        self.classifier = DocumentClassifier()

        self.builder = TableBuilder()

        self.article = ArticleParser()

        self.facture = FactureParser()

    def process(self, image_path):

        elements = self.engine.extraire_texte(image_path)

        texte = "\n".join(

            e["text"]

            for e in elements

        )

        document = self.classifier.detecter(

            texte

        )

        lignes = self.builder.build(elements)

        lignes = TableMerger().merge(lignes)

        # =====================================================
        # 4) Parser les articles
        # =====================================================

        articles = []

        for ligne in lignes:

            article = self.article.parse_line(ligne)

            if article:

                articles.append(article)

        data = {}

        if document == "FACTURE":

            data = self.facture.parse(

                texte,

                lignes

            )

            data["articles"] = articles

        return {

            "document": document,

            "texte": texte,

            "elements": elements,

            "lignes": lignes,

            "data": data

        }


pipeline = OCRPipeline()