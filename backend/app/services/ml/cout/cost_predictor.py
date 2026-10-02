import os
import joblib
import pandas as pd
from datetime import datetime

class CostPredictor:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        cost_model_path = os.path.join(base_dir, "cost_model.pkl")
        delay_days_path = os.path.abspath(os.path.join(base_dir, "..", "delai", "delay_days_model.pkl"))

        # Chargement du modèle de coût
        self.cost_model = None
        if os.path.exists(cost_model_path):
            try:
                self.cost_model = joblib.load(cost_model_path)
                print("[ML] Modèle de coût chargé avec succès.")
            except Exception as e:
                print(f"[ERREUR] Impossible de charger cost_model.pkl : {e}")

        # Chargement du modèle de délai en jours
        self.delay_days_model = None
        if os.path.exists(delay_days_path):
            try:
                self.delay_days_model = joblib.load(delay_days_path)
                print("[ML] Modèle de délai (jours) chargé avec succès.")
            except Exception as e:
                print(f"[ERREUR] Impossible de charger delay_days_model.pkl : {e}")

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

        # Récupération et nettoyage des valeurs saisies dans le formulaire
        materiel_str = str(materiel).strip().upper() or "PC PORTABLE"
        probleme_str = str(probleme).strip().upper() or "AUTRE"
        
        # Mapping intelligent basé sur ce que l'utilisateur a rempli dans ton formulaire :
        # Si la catégorie est vide, on l'associe au matériel
        cat_materiel = str(categorie).strip().upper() or materiel_str
        
        # Si l'utilisateur a renseigné des pièces suspectes (transmises via 'spec'), on les utilise
        spec_composant = str(spec).strip().upper() or "ORIGINAL"
        
        # Gamme par défaut si non précisée
        gamme_piece = str(gamme).strip().upper() or "COMPATIBLE / ADAPTABLE"
        
        # Type d'intervention choisi dans le menu déroulant du formulaire (ex: "Changement Pièce")
        type_intervention = str(type_inter).strip().upper() or "REMPLACEMENT MATÉRIEL"

        try:
            quantite = max(int(quantite), 1)
        except Exception:
            quantite = 1

        now = datetime.now()
        
        # DataFrame d'inférence avec les colonnes exactes du dataset d'entraînement
        input_df = pd.DataFrame([{
            "Matériel": materiel_str,
            "Categorie_Materiel": cat_materiel,
            "Problème": probleme_str,
            "Spec_Composant": spec_composant,
            "Gamme_Piece": gamme_piece,
            "Quantite": quantite,
            "Type_Intervention": type_intervention,
            "Réparé": "OUI",
            "Mois": now.month,
            "JourSemaine": now.weekday()
        }])

        print("🔍 [ML DEBUG] Données envoyées au modèle :", input_df.to_dict(orient="records"))

        # Prédiction Coût
        cout_estime = 150.0
        if self.cost_model is not None:
            try:
                cout_pred = self.cost_model.predict(input_df)[0]
                cout_estime = round(max(float(cout_pred), 0.0), 2)
            except Exception as e:
                print(f"[ML ERROR] Prédiction coût : {e}")

        # Prédiction Délai (Jours)
        delai_jours = 2
        if self.delay_days_model is not None:
            try:
                delai_pred = self.delay_days_model.predict(input_df)[0]
                delai_jours = int(round(max(float(delai_pred), 1.0)))
            except Exception as e:
                print(f"[ML ERROR] Prédiction délai : {e}")

        return {
            "cout_estime": cout_estime,
            "delai_estime": delai_jours
        }
    