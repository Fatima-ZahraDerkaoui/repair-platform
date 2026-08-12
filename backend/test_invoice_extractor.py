from pprint import pprint

from app.services.ocr.invoice_extractor import InvoiceExtractor


def test_invoice_extractor():

    print("\n" + "=" * 70)
    print("TEST COMPLET — INVOICE EXTRACTOR")
    print("=" * 70)

    extractor = InvoiceExtractor()

    # ==========================================================
    # DONNEES OCR SIMULEES
    # ==========================================================

    elements = [

        # ------------------------------------------------------
        # FACTURE
        # ------------------------------------------------------

        {
            "text": "FACTURE N° FAC-2026-001",
            "box": [100, 50, 350, 80]
        },

        {
            "text": "DATE : 10/08/2026",
            "box": [100, 90, 300, 120]
        },

        {
            "text": "FOURNISSEUR : HP MAROC",
            "box": [100, 130, 350, 160]
        },

        # ------------------------------------------------------
        # HEADER
        # ------------------------------------------------------

        {
            "text": "DESIGNATION",
            "box": [50, 200, 180, 225]
        },

        {
            "text": "REFERENCE",
            "box": [190, 200, 280, 225]
        },

        {
            "text": "QTE",
            "box": [290, 200, 330, 225]
        },

        {
            "text": "PU",
            "box": [340, 200, 400, 225]
        },

        {
            "text": "TOTAL",
            "box": [410, 200, 480, 225]
        },

        # ------------------------------------------------------
        # ARTICLE 1
        # ------------------------------------------------------

        {
            "text": "CARTOUCHE HP 652 BLACK",
            "box": [50, 250, 180, 275]
        },

        {
            "text": "HP-F6V25AE",
            "box": [190, 250, 280, 275]
        },

        {
            "text": "2",
            "box": [290, 250, 330, 275]
        },

        {
            "text": "215.00",
            "box": [340, 250, 400, 275]
        },

        {
            "text": "430.00",
            "box": [410, 250, 480, 275]
        },

        # ------------------------------------------------------
        # ARTICLE 2
        # ------------------------------------------------------

        {
            "text": "CARTOUCHE HP 652 COULEUR",
            "box": [50, 300, 180, 325]
        },

        {
            "text": "HP-F6V24AE",
            "box": [190, 300, 280, 325]
        },

        {
            "text": "1",
            "box": [290, 300, 330, 325]
        },

        {
            "text": "178.00",
            "box": [340, 300, 400, 325]
        },

        {
            "text": "178.00",
            "box": [410, 300, 480, 325]
        },

        # ------------------------------------------------------
        # FOOTER
        # ------------------------------------------------------

        {
            "text": "TOTAL HT",
            "box": [300, 400, 380, 425]
        },

        {
            "text": "608.00",
            "box": [410, 400, 480, 425]
        },

        {
            "text": "TOTAL TVA",
            "box": [300, 430, 380, 455]
        },

        {
            "text": "121.60",
            "box": [410, 430, 480, 455]
        },

        {
            "text": "TOTAL TTC",
            "box": [300, 460, 380, 485]
        },

        {
            "text": "729.60",
            "box": [410, 460, 480, 485]
        },
    ]

    # ==========================================================
    # EXTRACTION
    # ==========================================================

    try:

        result = extractor.extract(
            elements
        )

    except Exception as e:

        print("\n❌ ERREUR")

        print(
            f"Type : {type(e).__name__}"
        )

        print(
            f"Message : {e}"
        )

        raise

    # ==========================================================
    # RESULTAT
    # ==========================================================

    print("\nRESULTAT COMPLET :")

    pprint(
        result,
        sort_dicts=False
    )

    # ==========================================================
    # STRUCTURE
    # ==========================================================

    assert result is not None

    assert "articles" in result

    assert isinstance(
        result["articles"],
        list
    )

    print(
        "\n✓ Structure facture OK"
    )

    # ==========================================================
    # NUMERO
    # ==========================================================

    assert result["numero"] is not None

    print(
        f"✓ Numero : {result['numero']}"
    )

    # ==========================================================
    # DATE
    # ==========================================================

    assert result["date"] == "10/08/2026"

    print(
        f"✓ Date : {result['date']}"
    )

    # ==========================================================
    # ARTICLES
    # ==========================================================

    assert len(
        result["articles"]
    ) == 2

    print(
        f"✓ Nombre articles : "
        f"{len(result['articles'])}"
    )

    # ==========================================================
    # ARTICLE 1
    # ==========================================================

    article_1 = result["articles"][0]

    assert (
        article_1["reference"]
        == "HP-F6V25AE"
    )

    assert (
        article_1["designation"]
    )

    assert (
        article_1["quantite"]
        == 2
    )

    assert (
        article_1["prix_unitaire"]
        == 215.0
    )

    assert (
        article_1["total"]
        == 430.0
    )

    print(
        "✓ Article 1 OK"
    )

    # ==========================================================
    # ARTICLE 2
    # ==========================================================

    article_2 = result["articles"][1]

    assert (
        article_2["reference"]
        == "HP-F6V24AE"
    )

    assert (
        article_2["designation"]
    )

    assert (
        article_2["quantite"]
        == 1
    )

    assert (
        article_2["prix_unitaire"]
        == 178.0
    )

    assert (
        article_2["total"]
        == 178.0
    )

    print(
        "✓ Article 2 OK"
    )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    assert "validation" in result

    validation = result["validation"]

    assert isinstance(
        validation,
        dict
    )

    assert "score" in validation

    print(
        f"✓ Score validation : "
        f"{validation['score']}"
    )

    # ==========================================================
    # FIN
    # ==========================================================

    print("\n" + "=" * 70)
    print(
        "✓ TEST INVOICE EXTRACTOR PASSED"
    )
    print("=" * 70)


if __name__ == "__main__":
    test_invoice_extractor()