import json
import sys
from pathlib import Path

# ============================================================
# AJOUT RACINE DU PROJET
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ============================================================
# IMPORTS
# ============================================================

from app.services.ocr.ocr_engine import OCREngine
from app.services.ocr.column_detector import ColumnDetector
from app.services.ocr.column_classifier import ColumnClassifier
from app.services.ocr.line_builder import LineBuilder
from app.services.ocr.article_parser import ArticleParser
from app.services.ocr.facture_parser import FactureParser


# ============================================================
# CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# IMPORTANT :
# Remplacez ces chemins par vos deux images de test.
# ------------------------------------------------------------

FACTURE_ANCIEN_FORMAT = (
    ROOT_DIR /"backend" /"test_data" / "BL Facture.jpeg"
)

FACTURE_NOUVEAU_FORMAT = (
    ROOT_DIR / "backend" / "test_data" / "facture2.jpeg" 
)

OUTPUT_DIR = ROOT_DIR / "tests" / "results"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# AFFICHAGE
# ============================================================

def print_title(title):

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def print_subtitle(title):

    print()
    print("-" * 80)
    print(title)
    print("-" * 80)


# ============================================================
# AFFICHAGE ELEMENTS OCR
# ============================================================

def print_ocr_elements(elements):

    print_subtitle(
        f"OCR : {len(elements)} éléments détectés"
    )

    for i, element in enumerate(elements, start=1):

        print(
            f"[{i:03d}] "
            f"{element.get('text', '')!r} "
            f"| score={element.get('score', 0):.3f} "
            f"| box={element.get('box')}"
        )


# ============================================================
# AFFICHAGE COLONNES
# ============================================================

def print_columns(columns):

    print_subtitle("COLONNES DETECTEES")

    if not columns:

        print("Aucune colonne détectée.")

        return

    for column, x in columns.items():

        print(
            f"{column:15} -> X = {x:.2f}"
        )


# ============================================================
# AFFICHAGE CLASSIFICATION
# ============================================================

def print_classified(classified):

    print_subtitle(
        f"CLASSIFICATION : {len(classified)} éléments"
    )

    for i, element in enumerate(classified, start=1):

        print(
            f"[{i:03d}] "
            f"{element.get('text', '')!r:35} "
            f"| column={element.get('column'):12} "
            f"| x={element.get('x', 0):7.2f} "
            f"| y={element.get('y', 0):7.2f}"
        )


# ============================================================
# AFFICHAGE LIGNES / ARTICLES
# ============================================================

def print_linebuilder_result(groups):

    print_subtitle(
        f"LINE BUILDER : {len(groups)} article(s)"
    )

    for i, group in enumerate(groups, start=1):

        print()
        print(
            f"ARTICLE {i}"
        )

        print(
            f"Reference : "
            f"{group.get('reference')}"
        )

        print(
            f"Reference Y : "
            f"{group.get('reference_y')}"
        )

        elements = group.get(
            "elements",
            []
        )

        for element in elements:

            print(
                f"    "
                f"{element.get('text', '')!r:35} "
                f"| "
                f"{element.get('column', ''):12} "
                f"| x={element.get('x', 0):7.2f} "
                f"| y={element.get('y', 0):7.2f}"
            )


# ============================================================
# AFFICHAGE ARTICLES FINAUX
# ============================================================

def print_articles(articles):

    print_subtitle(
        f"ARTICLES FINAUX : {len(articles)}"
    )

    for i, article in enumerate(
        articles,
        start=1
    ):

        print()

        print(
            f"Article {i}"
        )

        print(
            f"  reference       : "
            f"{article.get('reference')}"
        )

        print(
            f"  designation     : "
            f"{article.get('designation')}"
        )

        print(
            f"  quantite        : "
            f"{article.get('quantite')}"
        )

        print(
            f"  prix_unitaire   : "
            f"{article.get('prix_unitaire')}"
        )

        print(
            f"  tva             : "
            f"{article.get('tva')}"
        )

        print(
            f"  total            : "
            f"{article.get('total')}"
        )


# ============================================================
# AFFICHAGE FACTURE
# ============================================================

def print_invoice(data):

    print_title(
        "RESULTAT FACTURE"
    )

    print(
        f"Numero      : "
        f"{data.get('numero')}"
    )

    print(
        f"Date        : "
        f"{data.get('date')}"
    )

    print(
        f"Client      : "
        f"{data.get('client')}"
    )

    print(
        f"Fournisseur : "
        f"{data.get('fournisseur')}"
    )

    print()

    print(
        f"Total HT    : "
        f"{data.get('total_ht')}"
    )

    print(
        f"Total TVA   : "
        f"{data.get('total_tva')}"
    )

    print(
        f"Total TTC   : "
        f"{data.get('total_ttc')}"
    )

    print()

    print_articles(
        data.get(
            "articles",
            []
        )
    )


# ============================================================
# SAUVEGARDE JSON
# ============================================================

def save_json(
    data,
    filename
):

    output_file = (
        OUTPUT_DIR / filename
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )

    print()
    print(
        f"JSON sauvegardé : "
        f"{output_file}"
    )


# ============================================================
# PIPELINE COMPLET
# ============================================================

def test_facture(
    image_path,
    nom_test
):

    print_title(
        f"TEST : {nom_test}"
    )

    # --------------------------------------------------------
    # Vérification fichier
    # --------------------------------------------------------

    if not image_path.exists():

        print(
            f"ERREUR : image introuvable : "
            f"{image_path}"
        )

        return None

    print(
        f"Image : {image_path}"
    )

    # --------------------------------------------------------
    # 1. OCR
    # --------------------------------------------------------

    print_title(
        "1. OCR"
    )

    ocr_engine = OCREngine()

    elements = (
        ocr_engine.extraire_texte(
            str(image_path)
        )
    )

    if not elements:

        print(
            "ERREUR : aucun élément OCR."
        )

        return None

    print_ocr_elements(
        elements
    )

    # --------------------------------------------------------
    # 2. DETECTION COLONNES
    # --------------------------------------------------------

    print_title(
        "2. COLUMN DETECTOR"
    )

    detector = ColumnDetector()

    columns = detector.detect(
        elements
    )

    print_columns(
        columns
    )

    # --------------------------------------------------------
    # 3. CLASSIFICATION
    # --------------------------------------------------------

    print_title(
        "3. COLUMN CLASSIFIER"
    )

    classifier = ColumnClassifier(
        columns
    )

    classified = classifier.classify(
        elements
    )

    print_classified(
        classified
    )

    # --------------------------------------------------------
    # 4. LINE BUILDER
    # --------------------------------------------------------

    print_title(
        "4. LINE BUILDER"
    )

    builder = LineBuilder()

    grouped_articles = builder.build(
        classified
    )

    print_linebuilder_result(
        grouped_articles
    )

    # --------------------------------------------------------
    # 5. ARTICLE PARSER
    # --------------------------------------------------------

    print_title(
        "5. ARTICLE PARSER"
    )

    article_parser = ArticleParser()

    articles = article_parser.parse(
        grouped_articles
    )

    print_articles(
        articles
    )

    # --------------------------------------------------------
    # 6. FACTURE PARSER
    # --------------------------------------------------------

    print_title(
        "6. FACTURE PARSER"
    )

    # --------------------------------------------------------
    # Texte complet OCR
    # --------------------------------------------------------

    texte_complet = (
        ocr_engine.texte_complet(
            str(image_path)
        )
    )

    facture_parser = FactureParser()

    facture = facture_parser.parse(
        texte_complet,
        articles
    )

    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    print_invoice(
        facture
    )

    # --------------------------------------------------------
    # Sauvegarde
    # --------------------------------------------------------

    save_json(
        facture,
        f"{nom_test}.json"
    )

    return facture


# ============================================================
# VERIFICATIONS AUTOMATIQUES
# ============================================================

def verify_result(
    result,
    nom_test
):

    print_title(
        f"VERIFICATION AUTOMATIQUE : {nom_test}"
    )

    if result is None:

        print(
            "❌ TEST IMPOSSIBLE"
        )

        return False

    errors = []

    # --------------------------------------------------------
    # Structure principale
    # --------------------------------------------------------

    required_fields = [
        "numero",
        "date",
        "client",
        "fournisseur",
        "total_ht",
        "total_tva",
        "total_ttc",
        "articles"
    ]

    for field in required_fields:

        if field not in result:

            errors.append(
                f"Champ absent : {field}"
            )

    # --------------------------------------------------------
    # Articles
    # --------------------------------------------------------

    articles = result.get(
        "articles",
        []
    )

    if not isinstance(
        articles,
        list
    ):

        errors.append(
            "articles n'est pas une liste"
        )

    else:

        for i, article in enumerate(
            articles,
            start=1
        ):

            required_article_fields = [
                "reference",
                "designation",
                "quantite",
                "prix_unitaire",
                "tva",
                "total"
            ]

            for field in required_article_fields:

                if field not in article:

                    errors.append(
                        f"Article {i}: "
                        f"champ absent {field}"
                    )

    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    if errors:

        print()

        print(
            "❌ ERREURS DETECTEES :"
        )

        for error in errors:

            print(
                f"   - {error}"
            )

        return False

    print(
        "✅ Structure correcte."
    )

    print(
        f"✅ {len(articles)} article(s) détecté(s)."
    )

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 80)
    print("       TEST COMPLET DU PIPELINE OCR FACTURE")
    print("=" * 80)

    print()
    print(
        "Deux formats sont testés :"
    )

    print(
        "  1. Ancien format"
    )

    print(
        "  2. Nouveau format avec REFERENCE"
    )

    # ========================================================
    # TEST ANCIEN FORMAT
    # ========================================================

    ancien = test_facture(
        FACTURE_ANCIEN_FORMAT,
        "facture_ancien_format"
    )

    ancien_ok = verify_result(
        ancien,
        "ANCIEN FORMAT"
    )

    # ========================================================
    # TEST NOUVEAU FORMAT
    # ========================================================

    nouveau = test_facture(
        FACTURE_NOUVEAU_FORMAT,
        "facture_nouveau_format"
    )

    nouveau_ok = verify_result(
        nouveau,
        "NOUVEAU FORMAT"
    )

    # ========================================================
    # RESULTAT GLOBAL
    # ========================================================

    print_title(
        "RESULTAT GLOBAL"
    )

    print(
        "Ancien format : "
        + (
            "✅ OK"
            if ancien_ok
            else "❌ ECHEC"
        )
    )

    print(
        "Nouveau format : "
        + (
            "✅ OK"
            if nouveau_ok
            else "❌ ECHEC"
        )
    )

    if ancien_ok and nouveau_ok:

        print()
        print(
            "🎉 TOUS LES TESTS SONT PASSES."
        )

    else:

        print()
        print(
            "⚠️ AU MOINS UN TEST A ECHOUE."
        )


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":

    main()