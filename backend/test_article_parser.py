from pprint import pprint

from app.services.ocr.article_parser import ArticleParser


def test_article_parser():
    parser = ArticleParser()

    # ==========================================================
    # TEST 1 — Format complet
    # ==========================================================

    ligne_1 = [
        {
            "column": "reference",
            "text": "HP-F6V25AE",
            "x": 100,
        },
        {
            "column": "designation",
            "text": "CARTOUCHE HP 652 BLACK",
            "x": 300,
        },
        {
            "column": "qte",
            "text": "2",
            "x": 600,
        },
        {
            "column": "pu",
            "text": "215.00",
            "x": 700,
        },
        {
            "column": "tva",
            "text": "20",
            "x": 800,
        },
        {
            "column": "total",
            "text": "430.00",
            "x": 900,
        },
    ]

    result_1 = parser.parse_line(ligne_1)

    print("\n" + "=" * 70)
    print("TEST 1 — ARTICLE COMPLET")
    print("=" * 70)
    pprint(result_1)

    assert result_1["reference"] == "HP-F6V25AE"
    assert result_1["designation"] == "CARTOUCHE HP 652 BLACK"
    assert result_1["quantite"] == 2
    assert result_1["prix_unitaire"] == 215.0
    assert result_1["tva"] == 20.0
    assert result_1["total"] == 430.0

    # ==========================================================
    # TEST 2 — Référence + désignation dans la même cellule
    # ==========================================================

    ligne_2 = [
        {
            "column": "designation",
            "text": "HP-F6V24AE - CARTOUCHE HP 652 COULEUR",
            "x": 300,
        },
        {
            "column": "qte",
            "text": "1",
            "x": 600,
        },
        {
            "column": "pu",
            "text": "178",
            "x": 700,
        },
        {
            "column": "total",
            "text": "178",
            "x": 900,
        },
    ]

    result_2 = parser.parse_line(ligne_2)

    print("\n" + "=" * 70)
    print("TEST 2 — REFERENCE DANS DESIGNATION")
    print("=" * 70)
    pprint(result_2)

    assert result_2["reference"] == "HP-F6V24AE"
    assert result_2["designation"] == "CARTOUCHE HP 652 COULEUR"
    assert result_2["quantite"] == 1
    assert result_2["prix_unitaire"] == 178.0
    assert result_2["total"] == 178.0

    # ==========================================================
    # TEST 3 — Désignation longue + texte parasite footer
    # ==========================================================

    ligne_3 = [
        {
            "column": "reference",
            "text": "HP-W2072A",
            "x": 100,
        },
        {
            "column": "designation",
            "text": (
                "TONER HP 117A LASER POUR 150/178/179A "
                "YELLOW"
            ),
            "x": 300,
        },
        {
            "column": "unknown",
            "text": (
                "N°SENE:100951068420/100951068634"
            ),
            "x": 400,
        },
        {
            "column": "unknown",
            "text": (
                "CASABLANCA A0522 45 02"
            ),
            "x": 450,
        },
        {
            "column": "qte",
            "text": "2",
            "x": 600,
        },
        {
            "column": "pu",
            "text": "680",
            "x": 700,
        },
        {
            "column": "tva",
            "text": "20",
            "x": 800,
        },
        {
            "column": "total",
            "text": "1360",
            "x": 900,
        },
        {
            "column": "unknown",
            "text": "TOTAL HT 2923.32",
            "x": 900,
        },
        {
            "column": "unknown",
            "text": "TOTAL TVA 584.68",
            "x": 900,
        },
        {
            "column": "unknown",
            "text": "TOTAL TTC 3508.00",
            "x": 900,
        },
    ]

    result_3 = parser.parse_line(ligne_3)

    print("\n" + "=" * 70)
    print("TEST 3 — DESIGNATION LONGUE + FOOTER")
    print("=" * 70)
    pprint(result_3)

    assert result_3["reference"] == "HP-W2072A"
    assert "TONER HP 117A" in result_3["designation"]
    assert result_3["quantite"] == 2
    assert result_3["prix_unitaire"] == 680.0
    assert result_3["total"] == 1360.0

    assert "TOTAL HT" not in result_3["designation"]
    assert "TOTAL TVA" not in result_3["designation"]
    assert "TOTAL TTC" not in result_3["designation"]

    # ==========================================================
    # TEST 4 — TVA absente
    # ==========================================================

    ligne_4 = [
        {
            "column": "reference",
            "text": "TATN324N",
            "x": 100,
        },
        {
            "column": "designation",
            "text": "TONER MINOLTA BIZHUB C258/454 TN 324/512 NOIR CET",
            "x": 300,
        },
        {
            "column": "qte",
            "text": "2",
            "x": 600,
        },
        {
            "column": "pu",
            "text": "300",
            "x": 700,
        },
        {
            "column": "total",
            "text": "600",
            "x": 900,
        },
    ]

    result_4 = parser.parse_line(ligne_4)

    print("\n" + "=" * 70)
    print("TEST 4 — TVA ABSENTE")
    print("=" * 70)
    pprint(result_4)

    assert result_4["reference"] == "TATN324N"
    assert result_4["quantite"] == 2
    assert result_4["prix_unitaire"] == 300.0
    assert result_4["tva"] is None
    assert result_4["total"] == 600.0

    # ==========================================================
    # TEST 5 — Quantité absente
    # ==========================================================

    ligne_5 = [
        {
            "column": "reference",
            "text": "TATN3210",
            "x": 100,
        },
        {
            "column": "designation",
            "text": "TONER MINOLTA BIZHUB C284 TN 321 COULEUR",
            "x": 300,
        },
        {
            "column": "pu",
            "text": "360",
            "x": 700,
        },
    ]

    result_5 = parser.parse_line(ligne_5)

    print("\n" + "=" * 70)
    print("TEST 5 — QUANTITE ABSENTE")
    print("=" * 70)
    pprint(result_5)

    assert result_5["reference"] == "TATN3210"
    assert result_5["designation"] == (
        "TONER MINOLTA BIZHUB C284 TN 321 COULEUR"
    )
    assert result_5["quantite"] is None
    assert result_5["prix_unitaire"] == 360.0
    assert result_5["total"] is None

    # ==========================================================
    # TEST 6 — Texte fournisseur parasite dans la ligne
    # ==========================================================

    ligne_6 = [
        {
            "column": "reference",
            "text": "CYAF1515",
            "x": 100,
        },
        {
            "column": "designation",
            "text": (
                "1, RUE DE STRASBOURG, KAMARIAT LAHRZK "
                "MAGASIN N°30"
            ),
            "x": 300,
        },
        {
            "column": "unknown",
            "text": (
                "ICE:001510053000094"
            ),
            "x": 350,
        },
        {
            "column": "qte",
            "text": "2",
            "x": 600,
        },
        {
            "column": "pu",
            "text": "120",
            "x": 700,
        },
        {
            "column": "tva",
            "text": "20",
            "x": 800,
        },
        {
            "column": "total",
            "text": "240",
            "x": 900,
        },
    ]

    result_6 = parser.parse_line(ligne_6)

    print("\n" + "=" * 70)
    print("TEST 6 — BRUIT FOURNISSEUR")
    print("=" * 70)
    pprint(result_6)

    assert result_6["reference"] == "CYAF1515"
    assert result_6["quantite"] == 2
    assert result_6["prix_unitaire"] == 120.0
    assert result_6["total"] == 240.0

    assert "ICE:" not in result_6["designation"]

    # ==========================================================
    # FIN
    # ==========================================================

    print("\n" + "=" * 70)
    print("TOUS LES TESTS ArticleParser SONT PASSES")
    print("=" * 70)


if __name__ == "__main__":
    test_article_parser()