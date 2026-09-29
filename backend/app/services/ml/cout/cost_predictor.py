import os
import joblib
import pandas as pd
from datetime import datetime


class CostPredictor:

    def __init__(self):

        base_dir = os.path.dirname(os.path.abspath(__file__))

        # ==============================
        # CHARGEMENT MODÈLE COÛT
        # ==============================

        cost_model_path = os.path.join(
            base_dir,
            "cost_model.pkl"
        )

        self.cost_model = None

        if os.path.exists(cost_model_path):
            try:
                self.cost_model = joblib.load(cost_model_path)
                print("[ML] Modèle de coût chargé avec succès.")

            except Exception as e:
                print(
                    f"[ERREUR] Impossible de charger "
                    f"cost_model.pkl : {e}"
                )

        else:
            print(
                f"[ERREUR] Modèle introuvable : "
                f"{cost_model_path}"
            )

        # ==============================
        # CHARGEMENT MODÈLE DÉLAI
        # ==============================

        delay_model_path = os.path.abspath(
            os.path.join(
                base_dir,
                "..",
                "delai",
                "delay_model.pkl"
            )
        )

        self.delay_model = None

        if os.path.exists(delay_model_path):
            try:
                self.delay_model = joblib.load(delay_model_path)
                print("[ML] Modèle de délai chargé avec succès.")

            except Exception as e:
                print(
                    f"[ERREUR] Impossible de charger "
                    f"delay_model.pkl : {e}"
                )

        else:
            print(
                f"[ERREUR] Modèle délai introuvable : "
                f"{delay_model_path}"
            )

    # =====================================================
    # PRÉDICTION
    # =====================================================

    def predict(
        self,
        materiel: str = "",
        probleme: str = "",
        categorie: str = "",
        spec: str = "",
        gamme: str = "",
        type_inter: str = "",
        quantite: int = 1
    ) -> dict:

        # ==============================
        # VALEURS DE SÉCURITÉ
        # ==============================

        materiel = str(materiel).strip() or "Inconnu"
        probleme = str(probleme).strip() or "Inconnu"

        categorie = (
            str(categorie).strip()
            or materiel
        )

        spec = (
            str(spec).strip()
            or "N/A"
        )

        gamme = (
            str(gamme).strip()
            or "N/A"
        )

        type_inter = (
            str(type_inter).strip()
            or "N/A"
        )

        try:
            quantite = max(int(quantite), 1)
        except Exception:
            quantite = 1

        # ==============================
        # FEATURES TEMPORELLES
        # ==============================

        now = datetime.now()

        mois = now.month
        jour_semaine = now.weekday()

        # ==============================
        # DATAFRAME
        # ==============================

        input_df = pd.DataFrame([{

            "Matériel": materiel,

            "Categorie_Materiel": categorie,

            "Problème": probleme,

            "Spec_Composant": spec,

            "Gamme_Piece": gamme,

            "Quantite": quantite,

            "Type_Intervention": type_inter,

            "Réparé": "OUI",

            "Mois": mois,

            "JourSemaine": jour_semaine

        }])

        # ==============================
        # DEBUG
        # ==============================

        print("\n================ ML INPUT ================")
        print(input_df.to_string(index=False))
        print("===========================================\n")

        # ==============================
        # PRÉDICTION COÛT
        # ==============================

        if self.cost_model is None:

            cout_estime = 150.0

        else:

            try:

                cout_pred = self.cost_model.predict(
                    input_df
                )[0]

                cout_estime = max(
                    float(cout_pred),
                    0.0
                )

                cout_estime = round(
                    cout_estime,
                    2
                )

            except Exception as e:

                print(
                    f"[ML ERROR] Prédiction coût : {e}"
                )

                cout_estime = 150.0

        # ==============================
        # PRÉDICTION DÉLAI
        # ==============================

        if self.delay_model is None:

            delai_pred = 0

        else:

            try:

                delai_pred = int(
                    self.delay_model.predict(
                        input_df
                    )[0]
                )

            except Exception as e:

                print(
                    f"[ML ERROR] Prédiction délai : {e}"
                )

                delai_pred = 0

        # ==============================
        # CONVERSION DÉLAI
        # ==============================

        delai_jours = 2 if delai_pred == 1 else 0

        # ==============================
        # RESULTAT
        # ==============================

        return {

            "cout_estime": cout_estime,

            "delai_estime": delai_jours

        }
    