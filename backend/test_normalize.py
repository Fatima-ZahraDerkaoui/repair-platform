from app.services.ocr.column_classifier import ColumnClassifier

tests = [

    "HP-F6V25AE",

    "EPST103BK",

    "CANGI490Y",

    "A125-45B",

    "ABC123",

    "LEN-100245",

    "Cartouche HP",

    "20%",

    "110.00"

]

for t in tests:

    print(

        f"{t:20}",

        "->",

        ColumnClassifier.score(t)

    )