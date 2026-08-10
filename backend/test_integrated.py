import sys
from pathlib import Path

# --------------------------------------------------------------
# IMPORTS
# --------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.ocr.line_builder import LineBuilder
from app.services.ocr.article_parser import ArticleParser


# ==============================================================
# OUTILS DE TEST
# ==============================================================

total_tests = 0
passed_tests = 0


def check(condition, message):
    global total_tests, passed_tests

    total_tests += 1

    if condition:
        passed_tests += 1
        print(f"[PASS] {message}")
    else:
        print(f"[FAIL] {message}")


def separator(title=None):

    print()
    print("=" * 70)

    if title:
        print(title)
        print("=" * 70)


def print_final_article(index, article):

    print()
    print("-" * 70)
    print(f"ARTICLE {index}")
    print("-" * 70)

    print(f"REFERENCE       : {article.get('reference')}")
    print(f"DESIGNATION     : {article.get('designation')}")
    print(f"QUANTITE        : {article.get('quantite')}")
    print(f"PRIX UNITAIRE   : {article.get('prix_unitaire')}")
    print(f"TVA             : {article.get('tva')}")
    print(f"TOTAL           : {article.get('total')}")


# ==============================================================
# CREATION ELEMENT OCR
# ==============================================================

def element(
    text,
    x,
    y,
    column
):

    return {
        "text": text,
        "x": x,
        "y": y,
        "column": column
    }


# ==============================================================
# TEST 1
# ANCIEN FORMAT
#
# HP-F6V25AE-Cartouche HP 652 Black
# 20%
# 215.00
# 2
# 430.00
# ==============================================================

def build_old_format_data():

    return [

        # ------------------------------------------------------
        # Article 1
        # ------------------------------------------------------

        element(
            "HP-F6V25AE-Cartouche HP 652 Black",
            260.5,
            578.5,
            "designation"
        ),

        element(
            "20%",
            795.5,
            588.0,
            "tva"
        ),

        element(
            "215.00",
            893.5,
            589.0,
            "pu"
        ),

        element(
            "2",
            1013.0,
            589.0,
            "qte"
        ),

        element(
            "430,00",
            1141.0,
            590.0,
            "total"
        ),

        # ------------------------------------------------------
        # Article 2
        # ------------------------------------------------------

        element(
            "HP-F6V24AE-Cartouche HP 652 Couleur",
            270.0,
            612.5,
            "designation"
        ),

        element(
            "20%",
            795.5,
            621.0,
            "tva"
        ),

        element(
            "178.00",
            895.0,
            621.5,
            "pu"
        ),

        element(
            "1",
            1012.5,
            621.5,
            "qte"
        ),

        element(
            "178.00",
            1143.0,
            622.0,
            "total"
        ),

        # ------------------------------------------------------
        # Article 3
        # ------------------------------------------------------

        element(
            "HP-CH561HE - Cartouche HP CH561 n°122 black - HP DESKJET",
            408.0,
            649.0,
            "designation"
        ),

        element(
            "20%",
            796.0,
            654.5,
            "tva"
        ),

        element(
            "190,00",
            895.5,
            655.5,
            "pu"
        ),

        element(
            "2",
            1014.0,
            655.0,
            "qte"
        ),

        element(
            "380.00",
            1143.5,
            655.0,
            "total"
        ),

        # ------------------------------------------------------
        # Article 4
        # ------------------------------------------------------

        element(
            "EPST103BK - (C13T00S14A) Bouteille d'encre Epson 103",
            407.5,
            705.5,
            "designation"
        ),

        element(
            "20%",
            797.0,
            709.5,
            "tva"
        ),

        element(
            "115,00",
            896.5,
            709.5,
            "pu"
        ),

        element(
            "2",
            1014.5,
            710.5,
            "qte"
        ),

        element(
            "230.00",
            1147.0,
            709.5,
            "total"
        ),

        # Continuation designation
        element(
            "L3150/L31111/L3110 Black",
            205.0,
            724.5,
            "designation"
        ),

        # ------------------------------------------------------
        # FIN FACTURE
        # ------------------------------------------------------

        element(
            "TOTAL HT",
            500.0,
            780.0,
            "designation"
        )
    ]


# ==============================================================
# TEST 2
# NOUVEAU FORMAT MAFOCOPI
# ==============================================================

def build_mafocopi_data():

    return [

        # ======================================================
        # ARTICLE 1
        # ======================================================

        element(
            "TATN324N",
            181.5,
            544.5,
            "reference"
        ),

        element(
            "TONER MINOLTA BIZHUB C 258/454",
            494.5,
            557.0,
            "designation"
        ),

        element(
            "IIC",
            977.0,
            545.5,
            "designation"
        ),

        element(
            "2",
            791.0,
            568.5,
            "qte"
        ),

        element(
            "300,00",
            1002.0,
            575.0,
            "pu"
        ),

        element(
            "TN 324/512 NOIR CET",
            430.0,
            577.0,
            "designation"
        ),

        element(
            "600,00",
            1166.0,
            582.0,
            "total"
        ),

        # ======================================================
        # ARTICLE 2
        # ======================================================

        element(
            "TTN324C",
            180.0,
            590.0,
            "reference"
        ),

        element(
            "TONER MINOLTA BIZHUB C258/454",
            492.5,
            601.5,
            "designation"
        ),

        element(
            "3",
            791.5,
            613.5,
            "qte"
        ),

        element(
            "R",
            718.5,
            614.0,
            "designation"
        ),

        element(
            "360.00",
            1002.0,
            618.5,
            "pu"
        ),

        element(
            "TN324/512 COUL/C/M/Y CETV",
            471.0,
            623.0,
            "designation"
        ),

        element(
            "1080,00",
            1160.5,
            624.0,
            "total"
        ),

        # ======================================================
        # ARTICLE 3
        # ======================================================

        element(
            "TATN321N",
            176.0,
            635.0,
            "reference"
        ),

        element(
            "TONER MINOLTA BIZHUB C 284 TN",
            499.0,
            647.0,
            "designation"
        ),

        element(
            "2",
            791.0,
            657.0,
            "qte"
        ),

        element(
            "300.00",
            1002.5,
            661.5,
            "pu"
        ),

        element(
            "321 NOIR CET",
            391.5,
            666.0,
            "designation"
        ),

        element(
            "600.00",
            1167.5,
            667.0,
            "total"
        ),

        # ======================================================
        # ARTICLE 4
        # ======================================================

        element(
            "TATN321CWT",
            191.0,
            681.0,
            "reference"
        ),

        element(
            "TONER MINOLTA BIZHUB C227 TN",
            484.5,
            690.5,
            "designation"
        ),

        element(
            "6",
            792.5,
            700.5,
            "qte"
        ),

        element(
            "290,00",
            1004.0,
            705.5,
            "pu"
        ),

        element(
            "1740.00",
            1161.0,
            711.0,
            "total"
        ),

        element(
            "321 COULEUR/2M/2Y/2G WT",
            456.5,
            712.5,
            "designation"
        ),

        # ======================================================
        # ARTICLE 5
        # ======================================================

        element(
            "TATN321O",
            171.0,
            728.0,
            "reference"
        ),

        element(
            "TONER MINOLTA BIZHUB C284TN",
            486.5,
            737.0,
            "designation"
        ),

        element(
            "360.00",
            1003.5,
            749.5,
            "pu"
        ),

        element(
            "720:00",
            1169.5,
            754.5,
            "total"
        ),

        element(
            "2",
            791.0,
            757.0,
            "qte"
        ),

        element(
            "321 COULEUR/2M CET",
            430.0,
            758.0,
            "designation"
        ),

        # ======================================================
        # ARTICLE 6
        # ======================================================

        element(
            "CYAF1515",
            167.5,
            772.5,
            "reference"
        ),

        element(
            "TAMBOUR RICOH AFICIO 1515 CET",
            489.0,
            782.5,
            "designation"
        ),

        element(
            "2",
            791.0,
            793.0,
            "qte"
        ),

        element(
            "120.00",
            1005.5,
            793.5,
            "pu"
        ),

        element(
            "240.00",
            1169.5,
            799.0,
            "total"
        ),

        # ------------------------------------------------------
        # FIN
        # ------------------------------------------------------

        element(
            "TOTAL TTC",
            500.0,
            850.0,
            "designation"
        )
    ]


# ==============================================================
# AFFICHAGE DES ELEMENTS PRODUITS PAR LINEBUILDER
# ==============================================================

def print_linebuilder_result(lines):

    print()
    print("RESULTAT LINEBUILDER")
    print("-" * 70)

    print(f"NOMBRE DE LIGNES : {len(lines)}")

    for i, line in enumerate(lines, 1):

        print()
        print(f"LIGNE {i}")
        print("-" * 50)

        for e in line:

            print(
                f"x={e.get('x', 0):7.1f} | "
                f"y={e.get('y', 0):7.1f} | "
                f"{e.get('column', ''):12} | "
                f"{e.get('text', '')}"
            )

# ==============================================================
# NORMALISATION SORTIE LINEBUILDER
# ==============================================================

def normalize_linebuilder_output(built):
    """
    Convertit toutes les sorties LineBuilder vers :

        List[List[dict]]

    Nouveau format :

        [
            {
                "reference": "TATN324N",
                "reference_y": 544.5,
                "elements": [...]
            }
        ]

    La référence présente au niveau du groupe est réinjectée
    dans les éléments afin que ArticleParser puisse la récupérer.
    """

    if not isinstance(built, list):
        return []

    normalized = []

    for group in built:

        # ======================================================
        # NOUVEAU FORMAT
        # ======================================================

        if isinstance(group, dict):

            elements = group.get("elements", [])

            if not isinstance(elements, list):
                elements = []

            # --------------------------------------------------
            # Récupération de la référence du groupe
            # --------------------------------------------------

            reference = group.get("reference")
            reference_y = group.get("reference_y")

            # --------------------------------------------------
            # Si une référence existe au niveau du groupe,
            # on la réinjecte dans les éléments.
            # --------------------------------------------------

            if reference:

                reference_element = {
                    "text": str(reference),
                    "x": 0,
                    "y": (
                        reference_y
                        if reference_y is not None
                        else 0
                    ),
                    "column": "reference"
                }

                # Éviter les doublons
                already_exists = any(
                    isinstance(e, dict)
                    and e.get("column") == "reference"
                    and str(e.get("text", "")).strip()
                    == str(reference).strip()
                    for e in elements
                )

                if not already_exists:

                    elements = [
                        reference_element,
                        *elements
                    ]

            normalized.append(elements)

        # ======================================================
        # ANCIEN FORMAT
        # ======================================================

        elif isinstance(group, list):

            normalized.append(group)

    return normalized

# ==============================================================
# RUN PIPELINE
# ==============================================================
def run_pipeline(
    classified,
    line_builder=None,
    article_parser=None,
    name="PIPELINE"
):

    # ==========================================================
    # COMPATIBILITE ANCIENS APPELS
    # ==========================================================

    # Exemple :
    # run_pipeline(classified, "ANCIEN FORMAT")
    if isinstance(line_builder, str):

        name = line_builder
        line_builder = None

    # ==========================================================
    # INSTANCIATION
    # ==========================================================

    if line_builder is None:
        line_builder = LineBuilder()

    if article_parser is None:
        article_parser = ArticleParser()

    # ==========================================================
    # TITRE
    # ==========================================================

    print()
    print("=" * 70)
    print(f"PIPELINE : {name}")
    print("=" * 70)

    print()
    print("OCR/Classified")
    print("      ↓")
    print("LineBuilder")
    print("      ↓")
    print("ArticleParser")
    print("      ↓")
    print("Articles")

    # ==========================================================
    # 1. LINEBUILDER
    # ==========================================================

    print()
    print("[1] LineBuilder.build()")

    built = line_builder.build(classified)

    print(f"Type résultat : {type(built)}")
    print(f"Nombre de groupes : {len(built)}")

    check(
        isinstance(built, list),
        "LineBuilder retourne une liste"
    )

    # ==========================================================
    # DEBUG STRUCTURE
    # ==========================================================

    if built:

        print(
            f"Type premier groupe : "
            f"{type(built[0])}"
        )

        if isinstance(built[0], dict):

            print("Format détecté : NOUVEAU FORMAT")

            print(
                f"Référence : "
                f"{built[0].get('reference', '')}"
            )

            print(
                f"Nombre éléments : "
                f"{len(built[0].get('elements', []))}"
            )

        elif isinstance(built[0], list):

            print("Format détecté : ANCIEN FORMAT")

            print(
                f"Nombre éléments : "
                f"{len(built[0])}"
            )

    # ==========================================================
    # 2. NORMALISATION
    # ==========================================================

    print()
    print("[2] Normalisation LineBuilder")

    lines = normalize_linebuilder_output(built)
    # ==========================================================
    # DEBUG REFERENCES
    # ==========================================================

    if lines:

        print()
        print("REFERENCES NORMALISEES")
        print("-" * 70)

        for i, line in enumerate(lines, 1):

            references = [
                e.get("text")
                for e in line
                if e.get("column") == "reference"
            ]

            print(
                f"Ligne {i} : "
                f"{references}"
            )

    print(
        f"Nombre de lignes normalisées : "
        f"{len(lines)}"
    )

    check(
        isinstance(lines, list),
        "Structure normalisée = liste"
    )

    if lines:

        check(
            isinstance(lines[0], list),
            "Chaque ligne normalisée est une liste"
        )

        if lines[0]:

            check(
                isinstance(lines[0][0], dict),
                "Chaque élément OCR est un dictionnaire"
            )

    # ==========================================================
    # 3. ARTICLEPARSER
    # ==========================================================

    print()
    print("[3] ArticleParser.parse()")

    articles = article_parser.parse(lines)

    print()
    print(
        f"Nombre d'articles finaux : "
        f"{len(articles)}"
    )

    check(
        isinstance(articles, list),
        "ArticleParser retourne une liste"
    )

    # ==========================================================
    # 4. AFFICHAGE
    # ==========================================================

    for i, article in enumerate(articles, 1):

        print_final_article(
            i,
            article
        )

    return articles

# ==============================================================
# TEST ANCIEN FORMAT
# ==============================================================

def test_old_format():

    separator(
        "TEST INTEGRE - ANCIEN FORMAT"
    )

    classified = build_old_format_data()

    articles = run_pipeline(
        classified,
        name="ANCIEN FORMAT HP / EPSON"
    )

    # ----------------------------------------------------------
    # Nombre
    # ----------------------------------------------------------

    check(
        len(articles) == 4,
        "Ancien format : 4 articles détectés"
    )

    if len(articles) >= 4:

        # ------------------------------------------------------
        # Article 1
        # ------------------------------------------------------

        a = articles[0]

        check(
            a["reference"] == "HP-F6V25AE",
            "Article 1 référence"
        )

        check(
            a["quantite"] == 2,
            "Article 1 quantité"
        )

        check(
            a["prix_unitaire"] == 215.0,
            "Article 1 prix unitaire"
        )

        check(
            a["tva"] == 20.0,
            "Article 1 TVA"
        )

        check(
            a["total"] == 430.0,
            "Article 1 total"
        )

        # ------------------------------------------------------
        # Article 2
        # ------------------------------------------------------

        a = articles[1]

        check(
            a["reference"] == "HP-F6V24AE",
            "Article 2 référence"
        )

        check(
            a["quantite"] == 1,
            "Article 2 quantité"
        )

        check(
            a["prix_unitaire"] == 178.0,
            "Article 2 prix unitaire"
        )

        check(
            a["total"] == 178.0,
            "Article 2 total"
        )

        # ------------------------------------------------------
        # Article 3
        # ------------------------------------------------------

        a = articles[2]

        check(
            a["reference"] == "HP-CH561HE",
            "Article 3 référence"
        )

        check(
            a["quantite"] == 2,
            "Article 3 quantité"
        )

        check(
            a["prix_unitaire"] == 190.0,
            "Article 3 prix unitaire"
        )

        check(
            a["total"] == 380.0,
            "Article 3 total"
        )

        # ------------------------------------------------------
        # Article 4
        # ------------------------------------------------------

        a = articles[3]

        check(
            a["reference"] == "EPST103BK",
            "Article 4 référence"
        )

        check(
            a["quantite"] == 2,
            "Article 4 quantité"
        )

        check(
            a["prix_unitaire"] == 115.0,
            "Article 4 prix unitaire"
        )

        check(
            a["tva"] == 20.0,
            "Article 4 TVA"
        )

        check(
            a["total"] == 230.0,
            "Article 4 total"
        )

        check(
            "L3150/L31111/L3110 Black"
            in a["designation"],
            "Article 4 continuation de désignation"
        )


# ==============================================================
# TEST MAFOCOPI
# ==============================================================

def test_mafocopi():

    separator(
        "TEST INTEGRE - MAFOCOPI"
    )

    classified = build_mafocopi_data()

    articles = run_pipeline(
        classified,
        name="NOUVEAU FORMAT MAFOCOPI"
    )

    # ----------------------------------------------------------
    # Nombre articles
    # ----------------------------------------------------------

    check(
        len(articles) == 6,
        "MAFOCOPI : 6 articles détectés"
    )

    if len(articles) >= 6:

        expected = [

            (
                "TATN324N",
                2,
                300.0,
                600.0
            ),

            (
                "TTN324C",
                3,
                360.0,
                1080.0
            ),

            (
                "TATN321N",
                2,
                300.0,
                600.0
            ),

            (
                "TATN321CWT",
                6,
                290.0,
                1740.0
            ),

            (
                "TATN321O",
                2,
                360.0,
                720.0
            ),

            (
                "CYAF1515",
                2,
                120.0,
                240.0
            )
        ]

        for i, (
            reference,
            quantity,
            price,
            total
        ) in enumerate(
            expected
        ):

            article = articles[i]

            check(
                article["reference"] == reference,
                f"MAFOCOPI article {i + 1} référence"
            )

            check(
                article["quantite"] == quantity,
                f"MAFOCOPI article {i + 1} quantité"
            )

            check(
                article["prix_unitaire"] == price,
                f"MAFOCOPI article {i + 1} prix"
            )

            check(
                article["total"] == total,
                f"MAFOCOPI article {i + 1} total"
            )


# ==============================================================
# TEST CONTINUATION DESIGNATION
# ==============================================================

def test_multiline_designation():

    separator(
        "TEST INTEGRE - DESIGNATION MULTI-LIGNE"
    )

    classified = [

        element(
            "HP-F6V25AE-Cartouche HP",
            250,
            500,
            "designation"
        ),

        element(
            "652 Black",
            250,
            520,
            "designation"
        ),

        element(
            "20%",
            800,
            510,
            "tva"
        ),

        element(
            "215.00",
            900,
            510,
            "pu"
        ),

        element(
            "2",
            1000,
            510,
            "qte"
        ),

        element(
            "430.00",
            1150,
            510,
            "total"
        ),

        element(
            "TOTAL HT",
            500,
            600,
            "designation"
        )
    ]

    articles = run_pipeline(
        classified,
        name="DESIGNATION MULTI-LIGNE"
    )

    check(
        len(articles) == 1,
        "Une seule ligne article"
    )

    if articles:

        article = articles[0]

        check(
            article["reference"] == "HP-F6V25AE",
            "Référence multi-ligne"
        )

        check(
            "Cartouche HP" in article["designation"],
            "Première partie désignation"
        )

        check(
            "652 Black" in article["designation"],
            "Deuxième partie désignation"
        )

        check(
            article["quantite"] == 2,
            "Quantité multi-ligne"
        )

        check(
            article["total"] == 430.0,
            "Total multi-ligne"
        )


# ==============================================================
# TEST VALEURS EUROPEENNES
# ==============================================================

def test_european_values():

    separator(
        "TEST INTEGRE - FORMATS NUMERIQUES"
    )

    classified = [

        element(
            "HP-F6V25AE-Cartouche HP",
            250,
            500,
            "designation"
        ),

        element(
            "20%",
            800,
            510,
            "tva"
        ),

        element(
            "1.250,50",
            900,
            510,
            "pu"
        ),

        element(
            "2",
            1000,
            510,
            "qte"
        ),

        element(
            "2.501,00",
            1150,
            510,
            "total"
        )
    ]

    articles = run_pipeline(
        classified,
        name="FORMATS EUROPEENS"
    )

    check(
        len(articles) == 1,
        "Format européen : 1 article"
    )

    if articles:

        article = articles[0]

        check(
            article["prix_unitaire"] == 1250.50,
            "Conversion 1.250,50"
        )

        check(
            article["total"] == 2501.00,
            "Conversion 2.501,00"
        )

        check(
            article["tva"] == 20.0,
            "Conversion TVA"
        )


# ==============================================================
# TEST STOP FACTURE
# ==============================================================

def test_stop_table():

    separator(
        "TEST INTEGRE - STOP FACTURE"
    )

    classified = [

        element(
            "HP-F6V25AE-Cartouche HP",
            250,
            500,
            "designation"
        ),

        element(
            "20%",
            800,
            510,
            "tva"
        ),

        element(
            "215.00",
            900,
            510,
            "pu"
        ),

        element(
            "2",
            1000,
            510,
            "qte"
        ),

        element(
            "430.00",
            1150,
            510,
            "total"
        ),

        # ------------------------------------------------------
        # STOP
        # ------------------------------------------------------

        element(
            "TOTAL HT",
            500,
            600,
            "designation"
        ),

        # ------------------------------------------------------
        # Ceci ne doit PAS être récupéré
        # ------------------------------------------------------

        element(
            "FAUSSE-REF-123",
            200,
            650,
            "designation"
        ),

        element(
            "999",
            1000,
            660,
            "qte"
        )
    ]

    articles = run_pipeline(
        classified,
        name="STOP TABLEAU"
    )

    check(
        len(articles) == 1,
        "Les éléments après TOTAL HT sont ignorés"
    )

    if articles:

        check(
            articles[0]["reference"]
            == "HP-F6V25AE",
            "Bonne référence avant le stop"
        )


# ==============================================================
# TEST REFERENCE DIRECTE
# ==============================================================

def test_direct_reference():

    separator(
        "TEST INTEGRE - REFERENCE DIRECTE"
    )

    classified = [

        element(
            "TTN324C",
            180,
            500,
            "reference"
        ),

        element(
            "TONER MINOLTA BIZHUB C258/454",
            450,
            505,
            "designation"
        ),

        element(
            "3",
            790,
            510,
            "qte"
        ),

        element(
            "360.00",
            1000,
            510,
            "pu"
        ),

        element(
            "1080.00",
            1160,
            510,
            "total"
        )
    ]

    articles = run_pipeline(
        classified,
        name="REFERENCE DIRECTE"
    )

    check(
        len(articles) == 1,
        "Reference directe : 1 article"
    )

    if articles:

        article = articles[0]

        check(
            article["reference"] == "TTN324C",
            "TTN324C correctement conservée"
        )

        check(
            article["quantite"] == 3,
            "TTN324C quantité"
        )

        check(
            article["prix_unitaire"] == 360.0,
            "TTN324C prix"
        )

        check(
            article["total"] == 1080.0,
            "TTN324C total"
        )


# ==============================================================
# TEST FINAL
# ==============================================================

def print_summary():

    separator(
        "RESULTAT GLOBAL"
    )

    print()
    print(
        f"Tests réussis : {passed_tests}/{total_tests}"
    )

    failed = total_tests - passed_tests

    print(
        f"Tests échoués : {failed}"
    )

    print()

    if failed == 0:

        print(
            "✓ TOUS LES TESTS INTEGRES SONT PASSES"
        )

    else:

        print(
            "✗ IL RESTE DES TESTS A CORRIGER"
        )


# ==============================================================
# MAIN
# ==============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("TEST INTEGRE LINEBUILDER + ARTICLEPARSER")
    print("=" * 70)

    print()
    print(
        "Pipeline testé :"
    )

    print(
        "OCR/Classified → LineBuilder → ArticleParser → Articles"
    )

    # ----------------------------------------------------------
    # Tests
    # ----------------------------------------------------------

    test_old_format()

    test_mafocopi()

    test_multiline_designation()

    test_european_values()

    test_stop_table()

    test_direct_reference()

    # ----------------------------------------------------------
    # Résultat
    # ----------------------------------------------------------

    print_summary()