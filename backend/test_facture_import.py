import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database.database import SessionLocal
from app.services.facture_import import import_facture_safe


JSON_FILE = (
    ROOT_DIR
    / "tests"
    / "results"
    / "facture_nouveau_format.json"
)


def main():

    if not JSON_FILE.exists():

        print(
            f"❌ Fichier introuvable : {JSON_FILE}"
        )

        return

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        facture_data = json.load(f)

    print("=" * 80)
    print("TEST IMPORT FACTURE OCR")
    print("=" * 80)

    print(
        f"Numéro : {facture_data.get('numero')}"
    )

    fournisseur = facture_data.get(
        "fournisseur",
        {}
    )

    print(
        f"Fournisseur : "
        f"{fournisseur.get('name')}"
    )

    print(
        f"Articles : "
        f"{len(facture_data.get('articles', []))}"
    )

    db = SessionLocal()

    try:

        success, facture, error = (
            import_facture_safe(
                db,
                facture_data
            )
        )

        if success:

            print()
            print("✅ IMPORT REUSSI")
            print(
                f"Facture ID : {facture.id}"
            )
            print(
                f"Numéro : {facture.numero}"
            )
            print(
                f"Fournisseur ID : "
                f"{facture.fournisseur_id}"
            )

        else:

            print()
            print("❌ IMPORT ECHOUE")
            print(
                f"Erreur : {error}"
            )

    finally:

        db.close()


if __name__ == "__main__":
    main()
    