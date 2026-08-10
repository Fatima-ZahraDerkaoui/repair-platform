from pprint import pprint

from app.services.ocr.invoice_validator import InvoiceValidator


def test_invoice_validator():

    validator = InvoiceValidator()

    # ==========================================================
    # TEST 1 — ARTICLE VALIDE
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 1 — ARTICLE VALIDE")
    print("=" * 70)

    article = {
        "reference": "HP-F6V25AE",
        "designation": "CARTOUCHE HP 652 BLACK",
        "quantite": 2,
        "prix_unitaire": 215.0,
        "tva": 20.0,
        "total": 430.0
    }

    errors = validator.validate_article(article)

    pprint(errors)

    assert errors == []

    print("✓ TEST 1 PASSED")


    # ==========================================================
    # TEST 2 — TOTAL ARTICLE INCORRECT
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 2 — TOTAL ARTICLE INCORRECT")
    print("=" * 70)

    article = {
        "reference": "HP-F6V24AE",
        "designation": "CARTOUCHE HP 652 COULEUR",
        "quantite": 2,
        "prix_unitaire": 178.0,
        "tva": 20.0,
        "total": 300.0
    }

    errors = validator.validate_article(article)

    pprint(errors)

    assert len(errors) == 1
    assert "total incorrect" in errors[0]

    print("✓ TEST 2 PASSED")


    # ==========================================================
    # TEST 3 — QUANTITE ABSENTE
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 3 — QUANTITE ABSENTE")
    print("=" * 70)

    article = {
        "reference": "TATN3210",
        "designation": "TONER MINOLTA BIZHUB C284 TN 321",
        "quantite": None,
        "prix_unitaire": 360.0,
        "tva": None,
        "total": None
    }

    errors = validator.validate_article(article)

    pprint(errors)

    assert "quantite absente" in errors
    assert "total absent" in errors

    print("✓ TEST 3 PASSED")


    # ==========================================================
    # TEST 4 — DESIGNATION VIDE
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 4 — DESIGNATION VIDE")
    print("=" * 70)

    article = {
        "reference": "CYAF1515",
        "designation": "",
        "quantite": 2,
        "prix_unitaire": 120.0,
        "tva": 20.0,
        "total": 240.0
    }

    errors = validator.validate_article(article)

    pprint(errors)

    assert "designation vide" in errors

    print("✓ TEST 4 PASSED")


    # ==========================================================
    # TEST 5 — TVA VALIDE
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 5 — TVA VALIDE")
    print("=" * 70)

    articles = [
        {
            "reference": "A001",
            "designation": "ARTICLE A",
            "quantite": 1,
            "prix_unitaire": 100,
            "tva": 0,
            "total": 100
        },
        {
            "reference": "A002",
            "designation": "ARTICLE B",
            "quantite": 1,
            "prix_unitaire": 100,
            "tva": 7,
            "total": 100
        },
        {
            "reference": "A003",
            "designation": "ARTICLE C",
            "quantite": 1,
            "prix_unitaire": 100,
            "tva": 10,
            "total": 100
        },
        {
            "reference": "A004",
            "designation": "ARTICLE D",
            "quantite": 1,
            "prix_unitaire": 100,
            "tva": 14,
            "total": 100
        },
        {
            "reference": "A005",
            "designation": "ARTICLE E",
            "quantite": 1,
            "prix_unitaire": 100,
            "tva": 20,
            "total": 100
        }
    ]

    errors = validator.validate_tva_values(articles)

    pprint(errors)

    assert errors == []

    print("✓ TEST 5 PASSED")


    # ==========================================================
    # TEST 6 — TVA INHABITUELLE
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 6 — TVA INHABITUELLE")
    print("=" * 70)

    articles = [
        {
            "reference": "A001",
            "designation": "ARTICLE A",
            "quantite": 1,
            "prix_unitaire": 100,
            "tva": 13,
            "total": 100
        }
    ]

    errors = validator.validate_tva_values(articles)

    pprint(errors)

    assert len(errors) == 1
    assert "TVA inhabituelle" in errors[0]

    print("✓ TEST 6 PASSED")


    # ==========================================================
    # TEST 7 — REFERENCES DUPLIQUEES
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 7 — REFERENCES DUPLIQUEES")
    print("=" * 70)

    articles = [
        {
            "reference": "HP-F6V25AE",
            "designation": "ARTICLE A",
            "quantite": 1,
            "prix_unitaire": 100,
            "tva": 20,
            "total": 100
        },
        {
            "reference": "HP-F6V25AE",
            "designation": "ARTICLE B",
            "quantite": 1,
            "prix_unitaire": 200,
            "tva": 20,
            "total": 200
        }
    ]

    errors = validator.validate_duplicate_reference(articles)

    pprint(errors)

    assert len(errors) == 1
    assert "Référence dupliquée" in errors[0]

    print("✓ TEST 7 PASSED")


    # ==========================================================
    # TEST 8 — REFERENCES DIFFERENTES
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 8 — REFERENCES DIFFERENTES")
    print("=" * 70)

    articles = [
        {
            "reference": "HP-F6V25AE",
            "designation": "ARTICLE A",
            "quantite": 1,
            "prix_unitaire": 100,
            "tva": 20,
            "total": 100
        },
        {
            "reference": "HP-F6V24AE",
            "designation": "ARTICLE B",
            "quantite": 1,
            "prix_unitaire": 200,
            "tva": 20,
            "total": 200
        }
    ]

    errors = validator.validate_duplicate_reference(articles)

    pprint(errors)

    assert errors == []

    print("✓ TEST 8 PASSED")


    # ==========================================================
    # TEST 9 — QUANTITE VALIDE
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 9 — QUANTITE VALIDE")
    print("=" * 70)

    articles = [
        {
            "reference": "A001",
            "designation": "ARTICLE",
            "quantite": 2,
            "prix_unitaire": 100,
            "tva": 20,
            "total": 200
        }
    ]

    errors = validator.validate_quantity(articles)

    pprint(errors)

    assert errors == []

    print("✓ TEST 9 PASSED")


    # ==========================================================
    # TEST 10 — QUANTITE ZERO
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 10 — QUANTITE ZERO")
    print("=" * 70)

    articles = [
        {
            "reference": "A001",
            "designation": "ARTICLE",
            "quantite": 0,
            "prix_unitaire": 100,
            "tva": 20,
            "total": 0
        }
    ]

    errors = validator.validate_quantity(articles)

    pprint(errors)

    assert len(errors) == 1
    assert "quantité <= 0" in errors[0]

    print("✓ TEST 10 PASSED")


    # ==========================================================
    # TEST 11 — QUANTITE TROP GRANDE
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 11 — QUANTITE SUSPECTE")
    print("=" * 70)

    articles = [
        {
            "reference": "A001",
            "designation": "ARTICLE",
            "quantite": 1500,
            "prix_unitaire": 100,
            "tva": 20,
            "total": 150000
        }
    ]

    errors = validator.validate_quantity(articles)

    pprint(errors)

    assert len(errors) == 1
    assert "quantité suspecte" in errors[0]

    print("✓ TEST 11 PASSED")


    # ==========================================================
    # TEST 12 — PRIX VALIDE
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 12 — PRIX VALIDE")
    print("=" * 70)

    articles = [
        {
            "reference": "A001",
            "designation": "ARTICLE",
            "quantite": 2,
            "prix_unitaire": 120,
            "tva": 20,
            "total": 240
        }
    ]

    errors = validator.validate_price(articles)

    pprint(errors)

    assert errors == []

    print("✓ TEST 12 PASSED")


    # ==========================================================
    # TEST 13 — PRIX NEGATIF
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 13 — PRIX NEGATIF")
    print("=" * 70)

    articles = [
        {
            "reference": "A001",
            "designation": "ARTICLE",
            "quantite": 2,
            "prix_unitaire": -120,
            "tva": 20,
            "total": -240
        }
    ]

    errors = validator.validate_price(articles)

    pprint(errors)

    assert len(errors) == 1
    assert "prix négatif" in errors[0]

    print("✓ TEST 13 PASSED")


    # ==========================================================
    # TEST 14 — HT + TVA = TTC
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 14 — HT + TVA = TTC")
    print("=" * 70)

    facture = {
        "total_ht": 1000.0,
        "total_tva": 200.0,
        "total_ttc": 1200.0
    }

    errors = validator.validate_amounts(facture)

    pprint(errors)

    assert errors == []

    print("✓ TEST 14 PASSED")


    # ==========================================================
    # TEST 15 — HT + TVA != TTC
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 15 — HT + TVA != TTC")
    print("=" * 70)

    facture = {
        "total_ht": 1000.0,
        "total_tva": 200.0,
        "total_ttc": 1300.0
    }

    errors = validator.validate_amounts(facture)

    pprint(errors)

    assert len(errors) == 1
    assert "HT + TVA" in errors[0]

    print("✓ TEST 15 PASSED")


    # ==========================================================
    # TEST 16 — CHAMPS OBLIGATOIRES
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 16 — CHAMPS OBLIGATOIRES")
    print("=" * 70)

    facture = {
        "numero": "FV2026-001",
        "date": "13/05/2026",
        "fournisseur": {
            "name": "CASINFO"
        },
        "articles": []
    }

    errors = validator.validate_required_fields(facture)

    pprint(errors)

    print(
        "\nATTENTION : avec le code actuel, "
        "'supplier' sera considéré manquant."
    )


    # ==========================================================
    # TEST 17 — VALIDATION COMPLETE
    # ==========================================================

    print("\n" + "=" * 70)
    print("TEST 17 — VALIDATION COMPLETE")
    print("=" * 70)

    facture = {
        "numero": "FV2026-05679",
        "date": "13/05/2026",

        "fournisseur": {
            "name": "CASINFO"
        },

        "articles": [
            {
                "reference": "HP-F6V25AE",
                "designation": "CARTOUCHE HP 652 BLACK",
                "quantite": 2,
                "prix_unitaire": 215.0,
                "tva": 20.0,
                "total": 430.0
            },
            {
                "reference": "HP-F6V24AE",
                "designation": "CARTOUCHE HP 652 COULEUR",
                "quantite": 1,
                "prix_unitaire": 178.0,
                "tva": None,
                "total": 178.0
            }
        ],

        "total_ht": 608.0,
        "total_tva": 121.6,
        "total_ttc": 729.6
    }

    result = validator.validate(facture)

    pprint(result)

    print("\nScore :", result["score"])

    print("Required :", result["required"])
    print("Amounts :", result["amounts"])
    print("References :", result["references"])
    print("TVA :", result["tva"])
    print("Designation :", result["designation"])
    print("Quantity :", result["quantity"])
    print("Price :", result["price"])
    print("Articles :", result["articles"])
    print("Invoice totals :", result["invoice_totals"])
    print("Line totals :", result["line_totals"])


    # ==========================================================
    # FIN
    # ==========================================================

    print("\n" + "=" * 70)
    print("TESTS INVOICEVALIDATOR TERMINES")
    print("=" * 70)


if __name__ == "__main__":
    test_invoice_validator()