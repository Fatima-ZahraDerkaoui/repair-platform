import os
import joblib
import pandas as pd

class CostPredictor:

    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Chargement du modèle de coût via Joblib
        cost_model_path = os.path.join(base_dir, "cost_model.pkl")
        if os.path.exists(cost_model_path):
            try:
                self.cost_model = joblib.load(cost_model_path)
            except Exception as e:
                print(f"[ERREUR] Impossible de charger cost_model.pkl: {e}")
                self.cost_model = None
        else:
            self.cost_model = None

        # Chargement du modèle de délai via Joblib
        delay_model_path = os.path.abspath(
            os.path.join(base_dir, "..", "delai", "delay_model.pkl")
        )
        if os.path.exists(delay_model_path):
            try:
                self.delay_model = joblib.load(delay_model_path)
            except Exception as e:
                print(f"[ERREUR] Impossible de charger delay_model.pkl: {e}")
                self.delay_model = None
        else:
            self.delay_model = None

    def predict(
        self,
        materiel: str = None,
        probleme: str = None,
        categorie: str = None,
        spec: str = "Écran Standard / LED",
        gamme: str = "Original",
        type_inter: str = "Remplacement Matériel",
        quantite: int = 1
    ) -> dict:
        """Prédit le coût (DH) et le délai en gérant les alias (materiel / categorie)."""
        
        # Si 'materiel' est fourni (depuis l'API), on l'utilise pour alimenter la catégorie ou le type
        cat_materiel = categorie or materiel or "PC Portable"
        prob = probleme or "Autre"

        # DataFrame au format exact attendu par la Pipeline entraînée
        input_df = pd.DataFrame([{
            'Categorie_Materiel': str(cat_materiel),
            'Problème': str(prob),
            'Spec_Composant': str(spec),
            'Gamme_Piece': str(gamme),
            'Type_Intervention': str(type_inter),
            'Quantite': int(quantite)
        }])

        # 1. Estimation du coût
        if self.cost_model:
            try:
                cout_pred = float(self.cost_model.predict(input_df)[0])
                cout_estime = round(max(cout_pred, 50.0), 2)
            except Exception as e:
                print(f"[ML ERROR] Écriture/Prédiction coût impossible : {e}")
                cout_estime = 150.0
        else:
            cout_estime = 150.0

        # 2. Estimation du délai
        if self.delay_model:
            try:
                delai_pred = str(self.delay_model.predict(input_df)[0])
            except Exception as e:
                print(f"[ML ERROR] Prédiction délai impossible : {e}")
                delai_pred = "Express (0-1j)"
        else:
            delai_pred = "Express (0-1j)"

        # Conversion du texte de délai en nombre entier de jours pour le schéma Pydantic
        # "Express (0-1j)" -> 1 jour, "Standard/Long (2j+)" -> 3 jours par exemple
        if "Express" in str(delai_pred):
            delai_jours = 1
        else:
            delai_jours = 3

        return {
            "cout_estime": cout_estime,
            "delai_estime": delai_jours
        }