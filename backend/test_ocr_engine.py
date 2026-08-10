from pathlib import Path
import sys


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

IMAGE_TEST = BASE_DIR / "test_data"/"BL Facture.jpeg"


# ============================================================
# IMPORTS
# ============================================================

try:
    from app.services.ocr.ocr_engine import OCREngine
except Exception as e:
    print(f"[FAIL] Import OCREngine : {e}")
    sys.exit(1)


# ============================================================
# OUTILS
# ============================================================

def afficher_resultat(condition, message):
    if condition:
        print(f"[PASS] {message}")
        return True
    else:
        print(f"[FAIL] {message}")
        return False


# ============================================================
# TEST 1 - INITIALISATION
# ============================================================

print("=" * 70)
print("TEST 1 - INITIALISATION OCRENGINE")
print("=" * 70)

tests_passes = 0
tests_total = 0


tests_total += 1

try:
    engine = OCREngine()

    if afficher_resultat(
        True,
        "OCREngine correctement initialisé"
    ):
        tests_passes += 1

except Exception as e:

    afficher_resultat(
        False,
        f"Initialisation OCREngine : {e}"
    )

    engine = None


# ============================================================
# TEST 1.1 - PADDLE OCR
# ============================================================

tests_total += 1

if engine is not None:

    if afficher_resultat(
        hasattr(engine, "ocr") and engine.ocr is not None,
        "Moteur PaddleOCR disponible"
    ):
        tests_passes += 1

else:

    print("[FAIL] Moteur PaddleOCR indisponible")


# ============================================================
# TEST 1.2 - PREPROCESSOR
# ============================================================

tests_total += 1

if engine is not None:

    if afficher_resultat(
        hasattr(engine, "preprocessor")
        and engine.preprocessor is not None,
        "ImagePreprocessor disponible"
    ):
        tests_passes += 1

else:

    print("[FAIL] ImagePreprocessor indisponible")


# ============================================================
# TEST 2 - IMAGE DE TEST
# ============================================================

print()
print("=" * 70)
print("TEST 2 - IMAGE DE TEST")
print("=" * 70)

print()
print(f"IMAGE : {IMAGE_TEST}")

tests_total += 1

if afficher_resultat(
    IMAGE_TEST.exists(),
    "Image de test existe"
):
    tests_passes += 1

    # ========================================================
    # TEST OCR REEL
    # ========================================================

    print()
    print("=" * 70)
    print("TEST 3 - OCR REEL")
    print("=" * 70)

    try:

        elements = engine.extraire_texte(
            str(IMAGE_TEST)
        )

        print()
        print(f"Nombre éléments OCR : {len(elements)}")

        tests_total += 1

        if afficher_resultat(
            isinstance(elements, list),
            "extraire_texte() retourne une liste"
        ):
            tests_passes += 1

        tests_total += 1

        if afficher_resultat(
            len(elements) > 0,
            "OCR détecte au moins un élément"
        ):
            tests_passes += 1

        # ----------------------------------------------------
        # Vérification structure
        # ----------------------------------------------------

        if elements:

            print()
            print("ELEMENTS OCR")
            print("-" * 70)

            for i, element in enumerate(elements, 1):

                print(
                    f"[{i}] "
                    f"text={element.get('text')!r} | "
                    f"score={element.get('score')} | "
                    f"box={element.get('box')}"
                )

            tests_total += 1

            structure_correcte = all(
                isinstance(e, dict)
                and "text" in e
                and "score" in e
                and "box" in e
                for e in elements
            )

            if afficher_resultat(
                structure_correcte,
                "Structure OCR correcte"
            ):
                tests_passes += 1

            # ------------------------------------------------
            # Vérification box
            # ------------------------------------------------

            tests_total += 1

            boxes_correctes = all(
                isinstance(e["box"], list)
                and len(e["box"]) == 4
                and all(
                    isinstance(v, int)
                    for v in e["box"]
                )
                for e in elements
            )

            if afficher_resultat(
                boxes_correctes,
                "Format des boxes correct"
            ):
                tests_passes += 1

            # ------------------------------------------------
            # Vérification scores
            # ------------------------------------------------

            tests_total += 1

            scores_corrects = all(
                isinstance(e["score"], float)
                and 0.0 <= e["score"] <= 1.0
                for e in elements
            )

            if afficher_resultat(
                scores_corrects,
                "Scores OCR valides"
            ):
                tests_passes += 1

        # ====================================================
        # TEST TEXTE COMPLET
        # ====================================================

        print()
        print("=" * 70)
        print("TEST 4 - TEXTE COMPLET")
        print("=" * 70)

        texte = engine.texte_complet(
            str(IMAGE_TEST)
        )

        print()
        print("TEXTE OCR")
        print("-" * 70)
        print(texte)

        tests_total += 1

        if afficher_resultat(
            isinstance(texte, str),
            "texte_complet() retourne une chaîne"
        ):
            tests_passes += 1

        tests_total += 1

        if afficher_resultat(
            len(texte.strip()) > 0,
            "texte_complet() contient du texte"
        ):
            tests_passes += 1

        # ====================================================
        # TEST BLOCS
        # ====================================================

        print()
        print("=" * 70)
        print("TEST 5 - BLOCS OCR")
        print("=" * 70)

        blocs = engine.extraire_blocs(
            str(IMAGE_TEST)
        )

        print()
        print(f"Nombre de blocs : {len(blocs)}")

        tests_total += 1

        if afficher_resultat(
            isinstance(blocs, list),
            "extraire_blocs() retourne une liste"
        ):
            tests_passes += 1

        if blocs:

            print()
            print("BLOCS")
            print("-" * 70)

            for i, bloc in enumerate(blocs, 1):

                print(
                    f"[{i}] "
                    f"text={bloc.get('text')!r} | "
                    f"score={bloc.get('score')} | "
                    f"box=("
                    f"{bloc.get('x1')}, "
                    f"{bloc.get('y1')}, "
                    f"{bloc.get('x2')}, "
                    f"{bloc.get('y2')}"
                    f")"
                )

            tests_total += 1

            structure_blocs_correcte = all(
                isinstance(b, dict)
                and "text" in b
                and "score" in b
                and "x1" in b
                and "y1" in b
                and "x2" in b
                and "y2" in b
                for b in blocs
            )

            if afficher_resultat(
                structure_blocs_correcte,
                "Structure des blocs correcte"
            ):
                tests_passes += 1

    except Exception as e:

        print()
        print("[FAIL] OCR réel")
        print(f"Erreur : {type(e).__name__}: {e}")


else:

    print()
    print(
        "[SKIP] Tests OCR réels non exécutés "
        "car l'image de test est absente."
    )


# ============================================================
# RESULTAT GLOBAL
# ============================================================

print()
print("=" * 70)
print("RESULTAT GLOBAL")
print("=" * 70)

print()
print(
    f"Tests réussis : {tests_passes}/{tests_total}"
)

print(
    f"Tests échoués : {tests_total - tests_passes}"
)

print()

if tests_passes == tests_total:

    print("✓ TOUS LES TESTS OCRENGINE SONT PASSES")

else:

    print("✗ IL RESTE DES TESTS OCRENGINE A CORRIGER")
