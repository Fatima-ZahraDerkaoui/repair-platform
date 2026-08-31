import os
import pickle
import pandas as pd


class CostPredictor:

    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Chargement du modèle de coût
        cost_model_path = os.path.join(base_dir, "cost_model.pkl")
        if os.path.exists(cost_model_path):
            with open(cost_model_path, "rb") as f:
                self.cost_model = pickle.load(f)
        else:
            self.cost_model = None

        # Chargement du modèle de délai
        delay_model_path = os.path.abspath(
            os.path.join(base_dir, "..", "delai", "delay_model.pkl")
        )
        if os.path.exists(delay_model_path):
            with open(delay_model_path, "rb") as f:
                self.delay_model = pickle.load(f)
        else:
            self.delay_model = None

    def predict(self, materiel: str, probleme: str) -> dict:
        """Prédit le coût (DH) et le délai (Jours) pour un matériel et un problème donnés."""
        input_df = pd.DataFrame([{
            "Matériel": str(materiel or "Machine"),
            "Problème": str(probleme or "Entretien")
        }])

        # 1. Coût estimé
        if self.cost_model:
            cout_pred = float(self.cost_model.predict(input_df)[0])
            cout_estime = round(max(cout_pred, 50.0), 2)
        else:
            cout_estime = 150.0

        # 2. Délai estimé
        if self.delay_model:
            delai_pred = float(self.delay_model.predict(input_df)[0])
            delai_estime = max(int(round(delai_pred)), 1)
        else:
            delai_estime = 1

        return {
            "cout_estime": cout_estime,
            "delai_estime": delai_estime
        }
    