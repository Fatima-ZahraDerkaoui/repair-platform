from app.services.ocr.article_parser import ArticleParser

parser = ArticleParser()

print("=" * 70)
print("TEST is_reference()")
print("=" * 70)

tests = [

    "HP-F6V25AE",
    "EPST103BK",
    "EPST103C",
    "EPST103M",
    "EPST103Y",
    "CANGI490M",
    "CANGI490Y",
    "LEN-100245",
    "A125-45B",
    "Cartouche HP",
    "20%",
    "110.00"

]

for t in tests:

    print(f"{t:25} -> {parser.is_reference(t)}")


print()
print("=" * 70)
print("TEST split_reference()")
print("=" * 70)

designations = [

    "HP-F6V25AE-Cartouche HP 652 Black",

    "HP-CH561HE-Cartouche HP CH561 noir",

    "EPST103BK-(C13T00S14A) Bouteille d'encre Epson",

    "EPST103C-(C13T00S24A) Bouteille Epson Cyan",

    "EPST103M-(C13T00S34A) Bouteille Epson Magenta",

    "EPST103Y-(C13T00S44A) Bouteille Epson Yellow",

    "CANGI490M-CARTOUCHE CANON GI-490 MAGENTA",

    "CANGI490Y-CARTOUCHE CANON GI490YELLOW",

    "LEN-100245 Laptop Lenovo",

    "Cartouche HP"

]

for texte in designations:

    ref, des = parser.split_reference(texte)

    print()
    print("Texte       :", texte)
    print("Reference   :", ref)
    print("Designation :", des)


print()
print("=" * 70)
print("TEST parse_line()")
print("=" * 70)

ligne = [

    {
        "column": "designation",
        "text": "EPST103BK-(C13T00S14A) Bouteille d'encre Epson"
    },

    {
        "column": "designation",
        "text": "L3150/L31111/L3110 Black"
    },

    {
        "column": "tva",
        "text": "20%"
    },

    {
        "column": "pu",
        "text": "115,00"
    },

    {
        "column": "qte",
        "text": "2"
    },

    {
        "column": "total",
        "text": "230.00"
    }

]

article = parser.parse_line(ligne)

print()

for k, v in article.items():

    print(f"{k:15}: {v}")


print()
print("=" * 70)
print("TEST Canon")
print("=" * 70)

ligne = [

    {
        "column": "designation",
        "text": "CANGI490M-CARTOUCHE CANON GI-490 MAGENTA"
    },

    {
        "column": "tva",
        "text": "20%"
    },

    {
        "column": "pu",
        "text": "90,00"
    },

    {
        "column": "qte",
        "text": "2"
    },

    {
        "column": "total",
        "text": "180.00"
    }

]

article = parser.parse_line(ligne)

print()

for k, v in article.items():

    print(f"{k:15}: {v}")


print()
print("=" * 70)
print("TEST HP")
print("=" * 70)

ligne = [

    {
        "column": "designation",
        "text": "HP-F6V25AE-Cartouche HP 652 Black"
    },

    {
        "column": "designation",
        "text": "1050/2050/2050S"
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
    