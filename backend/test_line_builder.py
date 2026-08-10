from app.services.ocr.line_builder import LineBuilder


# ==========================================================
# OUTILS AFFICHAGE
# ==========================================================

def print_separator():
    print("=" * 70)

def print_article(article, number):

    print()
    print("=" * 70)
    print(f"ARTICLE {number}")
    print("=" * 70)

    print(
        f"REFERENCE       : "
        f"{article.get('reference', '')}"
    )

    elements = article.get(
        "elements",
        []
    )

    print(
        f"NOMBRE ELEMENTS : "
        f"{len(elements)}"
    )

    for element in elements:

        print(
            f"x={element.get('x', 0):7.1f} | "
            f"y={element.get('y', 0):7.1f} | "
            f"{element.get('column', ''):12} | "
            f"{element.get('text', '')}"
        )
        

# ==========================================================
# TEST 1 : REFERENCES
# ==========================================================

def test_references(builder):

    print_separator()
    print("TEST REFERENCE")
    print_separator()

    references = [

        "HP-F6V25AE",
        "EPST103BK",
        "CANGI490M",

        "TTN324N",
        "TTN324C",

        "TATN321N",
        "TATN321CWT",

        "TTN321O",

        "CYAF1515",

        "LEN-100245",
        "A125-45B",

        # Ne doivent PAS être des références
        "Cartouche",
        "HP",
        "20%",
        "300.00",
        "REFERENCE",
        "TOTAL",
    ]

    for reference in references:

        result = builder.is_reference(
            reference
        )

        print(
            f"{reference:20} "
            f"-> is_reference = {result}"
        )


# ==========================================================
# TEST 2 : ANCIEN FORMAT
# ==========================================================

def test_old_format(builder):

    print()
    print_separator()
    print("TEST ANCIEN FORMAT")
    print_separator()

    classified = [

        # --------------------------------------------------
        # ARTICLE 1
        # --------------------------------------------------

        {
            "text": "HP-F6V25AE-Cartouche HP 652 Black",
            "x": 260.5,
            "y": 578.5,
            "column": "designation",
        },

        {
            "text": "20%",
            "x": 795.5,
            "y": 588.0,
            "column": "tva",
        },

        {
            "text": "215.00",
            "x": 893.5,
            "y": 589.0,
            "column": "pu",
        },

        {
            "text": "2",
            "x": 1013.0,
            "y": 589.0,
            "column": "qte",
        },

        {
            "text": "430,00",
            "x": 1141.0,
            "y": 590.0,
            "column": "total",
        },

        # --------------------------------------------------
        # ARTICLE 2
        # --------------------------------------------------

        {
            "text": "HP-F6V24AE-Cartouche HP 652 Couleur",
            "x": 270.0,
            "y": 612.5,
            "column": "designation",
        },

        {
            "text": "20%",
            "x": 795.5,
            "y": 621.0,
            "column": "tva",
        },

        {
            "text": "178.00",
            "x": 895.0,
            "y": 621.5,
            "column": "pu",
        },

        {
            "text": "1",
            "x": 1012.5,
            "y": 621.5,
            "column": "qte",
        },

        {
            "text": "178.00",
            "x": 1143.0,
            "y": 622.0,
            "column": "total",
        },

        # --------------------------------------------------
        # ARTICLE 3
        # --------------------------------------------------

        {
            "text": "HP-CH561HE - Cartouche HP CH561 n°122 black - HP DESKJET",
            "x": 408.0,
            "y": 649.0,
            "column": "designation",
        },

        {
            "text": "20%",
            "x": 796.0,
            "y": 654.5,
            "column": "tva",
        },

        {
            "text": "190,00",
            "x": 895.5,
            "y": 655.5,
            "column": "pu",
        },

        {
            "text": "2",
            "x": 1014.0,
            "y": 655.0,
            "column": "qte",
        },

        {
            "text": "380.00",
            "x": 1143.5,
            "y": 655.0,
            "column": "total",
        },

        # --------------------------------------------------
        # ARTICLE 4
        # --------------------------------------------------

        {
            "text": "EPST103BK - (C13T00S14A) Bouteille d'encre Epson 103",
            "x": 407.5,
            "y": 705.5,
            "column": "designation",
        },

        {
            "text": "20%",
            "x": 797.0,
            "y": 709.5,
            "column": "tva",
        },

        {
            "text": "115,00",
            "x": 896.5,
            "y": 709.5,
            "column": "pu",
        },

        {
            "text": "2",
            "x": 1014.5,
            "y": 710.5,
            "column": "qte",
        },

        {
            "text": "230.00",
            "x": 1147.0,
            "y": 709.5,
            "column": "total",
        },

        {
            "text": "L3150/L31111/L3110 Black",
            "x": 205.0,
            "y": 724.5,
            "column": "designation",
        },

    ]

    articles = builder.build(
        classified
    )
    print("\nDEBUG TYPE RESULT")
    print("type articles :", type(articles))

    if articles:
        print("type article[0] :", type(articles[0]))
        print("article[0] :", articles[0])

    print()
    print(
        f"NOMBRE D'ARTICLES : "
        f"{len(articles)}"
    )

    for i, article in enumerate(
        articles,
        1
    ):

        print_article(
            article,
            i
        )


# ==========================================================
# TEST 3 : NOUVEAU FORMAT MAFOCOPI
# ==========================================================

def test_mafocopi(builder):

    print()
    print_separator()
    print("TEST NOUVEAU FORMAT MAFOCOPI")
    print_separator()

    classified = [

        # ==================================================
        # ARTICLE 1
        # ==================================================

        {
            "text": "TATN324N",
            "x": 181.5,
            "y": 544.5,
            "column": "reference",
        },

        {
            "text": "TONER MINOLTA BIZHUB C 258/454",
            "x": 494.5,
            "y": 557.0,
            "column": "designation",
        },

        {
            "text": "TN 324/512 NOIR CET",
            "x": 430.0,
            "y": 577.0,
            "column": "designation",
        },

        {
            "text": "IIC",
            "x": 977.0,
            "y": 545.5,
            "column": "designation",
        },

        {
            "text": "2",
            "x": 791.0,
            "y": 568.5,
            "column": "qte",
        },

        {
            "text": "300,00",
            "x": 1002.0,
            "y": 575.0,
            "column": "pu",
        },

        {
            "text": "600,00",
            "x": 1166.0,
            "y": 582.0,
            "column": "total",
        },

        # ==================================================
        # ARTICLE 2
        # ==================================================

        {
            "text": "TTN324C",
            "x": 180.0,
            "y": 590.0,
            "column": "reference",
        },

        {
            "text": "TONER MINOLTA BIZHUB C258/454",
            "x": 492.5,
            "y": 601.5,
            "column": "designation",
        },

        {
            "text": "TN324/512 COUL/C/M/Y CETV",
            "x": 471.0,
            "y": 623.0,
            "column": "designation",
        },

        {
            "text": "R",
            "x": 718.5,
            "y": 614.0,
            "column": "designation",
        },

        {
            "text": "3",
            "x": 791.5,
            "y": 613.5,
            "column": "qte",
        },

        {
            "text": "360.00",
            "x": 1002.0,
            "y": 618.5,
            "column": "pu",
        },

        {
            "text": "1080,00",
            "x": 1160.5,
            "y": 624.0,
            "column": "total",
        },

        # ==================================================
        # ARTICLE 3
        # ==================================================

        {
            "text": "TATN321N",
            "x": 176.0,
            "y": 635.0,
            "column": "reference",
        },

        {
            "text": "TONER MINOLTA BIZHUB C 284 TN",
            "x": 499.0,
            "y": 647.0,
            "column": "designation",
        },

        {
            "text": "321 NOIR CET",
            "x": 391.5,
            "y": 666.0,
            "column": "designation",
        },

        {
            "text": "2",
            "x": 791.0,
            "y": 657.0,
            "column": "qte",
        },

        {
            "text": "300.00",
            "x": 1002.5,
            "y": 661.5,
            "column": "pu",
        },

        {
            "text": "600.00",
            "x": 1167.5,
            "y": 667.0,
            "column": "total",
        },

        # ==================================================
        # ARTICLE 4
        # ==================================================

        {
            "text": "TATN321CWT",
            "x": 191.0,
            "y": 681.0,
            "column": "reference",
        },

        {
            "text": "TONER MINOLTA BIZHUB C227 TN",
            "x": 484.5,
            "y": 690.5,
            "column": "designation",
        },

        {
            "text": "321 COULEUR/2M/2Y/2G WT",
            "x": 456.5,
            "y": 712.5,
            "column": "designation",
        },

        {
            "text": "6",
            "x": 792.5,
            "y": 700.5,
            "column": "qte",
        },

        {
            "text": "290,00",
            "x": 1004.0,
            "y": 705.5,
            "column": "pu",
        },

        {
            "text": "1740.00",
            "x": 1161.0,
            "y": 711.0,
            "column": "total",
        },

        # ==================================================
        # ARTICLE 5
        # ==================================================

        {
            "text": "TATN321O",
            "x": 171.0,
            "y": 728.0,
            "column": "reference",
        },

        {
            "text": "TONER MINOLTA BIZHUB C284TN",
            "x": 486.5,
            "y": 737.0,
            "column": "designation",
        },

        {
            "text": "321 COULEUR/2M CET",
            "x": 430.0,
            "y": 758.0,
            "column": "designation",
        },

        {
            "text": "2",
            "x": 791.0,
            "y": 757.0,
            "column": "qte",
        },

        {
            "text": "360.00",
            "x": 1003.5,
            "y": 749.5,
            "column": "pu",
        },

        {
            "text": "720:00",
            "x": 1169.5,
            "y": 754.5,
            "column": "total",
        },

        # ==================================================
        # ARTICLE 6
        # ==================================================

        {
            "text": "CYAF1515",
            "x": 167.5,
            "y": 772.5,
            "column": "reference",
        },

        {
            "text": "TAMBOUR RICOH AFICIO 1515 CET",
            "x": 489.0,
            "y": 782.5,
            "column": "designation",
        },

        {
            "text": "2",
            "x": 791.0,
            "y": 793.0,
            "column": "qte",
        },

        {
            "text": "120.00",
            "x": 1005.5,
            "y": 793.5,
            "column": "pu",
        },

        {
            "text": "240.00",
            "x": 1169.5,
            "y": 799.0,
            "column": "total",
        },
    ]

    articles = builder.build(
        classified
    )

    print()
    print(
        f"NOMBRE D'ARTICLES : "
        f"{len(articles)}"
    )

    for i, article in enumerate(
        articles,
        1
    ):

        print_article(
            article,
            i
        )


# ==========================================================
# TEST 4 : EXTRACTION REFERENCE
# ==========================================================

def test_extract_reference(builder):

    print()
    print_separator()
    print("TEST EXTRACTION REFERENCE")
    print_separator()

    texts = [

        "HP-F6V25AE-Cartouche HP 652 Black",

        "EPST103BK - Bouteille d'encre Epson",

        "CANGI490M-CARTOUCHE CANON GI-490 MAGENTA",

        "TTN324N",

        "TATN321CWT",

        "CYAF1515",

        "Cartouche HP",

        "300.00",

        "20%",
    ]

    for text in texts:

        reference = (
            builder.extract_reference_from_text(
                text
            )
        )

        print(
            f"{text:55} "
            f"-> {reference}"
        )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print()
    print_separator()
    print("TEST LINE BUILDER")
    print_separator()

    builder = LineBuilder(
        tolerance_y=18
    )

    # ------------------------------------------------------
    # TEST REFERENCES
    # ------------------------------------------------------

    test_references(
        builder
    )

    # ------------------------------------------------------
    # TEST EXTRACTION
    # ------------------------------------------------------

    test_extract_reference(
        builder
    )

    # ------------------------------------------------------
    # TEST ANCIEN FORMAT
    # ------------------------------------------------------

    test_old_format(
        builder
    )

    # ------------------------------------------------------
    # TEST MAFOCOPI
    # ------------------------------------------------------

    test_mafocopi(
        builder
    )

    print()
    print_separator()
    print("FIN DU TEST")
    print_separator()