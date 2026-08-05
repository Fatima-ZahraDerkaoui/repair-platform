from app.services.ocr.article_parser import ArticleParser

parser = ArticleParser()

ligne = [

    {

        "column": "designation",

        "text": "HP-F6V25AE-Cartouche HP 652 Black"

    },

    {

        "column": "tva",

        "text": "20%"

    },

    {

        "column": "pu",

        "text": "215.00"

    },

    {

        "column": "qte",

        "text": "2"

    },

    {

        "column": "total",

        "text": "430.00"

    }

]

article = parser.parse_line(ligne)

print()

for k, v in article.items():

    print(f"{k:15}: {v}")