import os
import re
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.pipeline import Pipeline


def normaliser_chaine(txt: str) -> str:
    """Normalise le texte pour extraire les mots-clés essentiels."""
    if pd.isna(txt):
        return ""
    txt = str(txt).upper().strip()
    txt = re.sub(r'[^A-Z0-9\s]', ' ', txt)
    return " ".join(txt.split())


def entrainer_et_sauvegarder():
    # 1. Chargement du fichier
    data_path = os.path.join("data", "REPARATION.xlsx")
    if not os.path.exists(data_path):
        data_path = os.path.join("data", "REPARATION_clean.xlsx")

    print(f"[ML FINAL] Lecture des données depuis : {data_path}")
    df = pd.read_excel(data_path)
    df.columns = [str(col).strip() for col in df.columns]

    # Nettoyage des dates & délais
    df['Date Entrée'] = pd.to_datetime(df['Date Entrée'], errors='coerce')
    df['Date Sortie'] = pd.to_datetime(df['Date Sortie'], errors='coerce')
    
    # Délai calculé (borné entre 1 et 10 jours)
    df['Delai_Jours'] = (df['Date Sortie'] - df['Date Entrée']).dt.days
    df['Delai_Jours'] = df['Delai_Jours'].apply(
        lambda x: int(x) if pd.notnull(x) and 1 <= x <= 10 else 1
    )

    # Nettoyage des montants
    def parse_montant(val):
        if pd.isna(val):
            return 0.0
        val_str = str(val).replace(' ', '').replace(',', '.').replace('DH', '')
        try:
            return float(val_str)
        except ValueError:
            return 0.0

    df['Montant_Clean'] = df['Montant'].apply(parse_montant)

    # Filtrer les données valides
    df_clean = df[
        (df['Réparé'].astype(str).str.upper().str.contains('OUI')) &
        (df['Montant_Clean'] > 0)
    ].copy()

    # Construction de la feature textuelle enrichie
    df_clean['Feature_Text'] = (
        df_clean['Matériel'].apply(normaliser_chaine) + " " +
        df_clean['Problème'].apply(normaliser_chaine)
    )

    X = df_clean['Feature_Text']
    y_cout = df_clean['Montant_Clean']
    y_delai = df_clean['Delai_Jours']

    # 2. Modèle de Coût (Extra Trees Regressor pour limiter l'overfitting)
    cost_pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(ngram_range=(1, 2), max_features=200)),
        ('regressor', ExtraTreesRegressor(n_estimators=100, random_state=42))
    ])
    cost_pipeline.fit(X, y_cout)

    # 3. Modèle de Délai
    delay_pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(ngram_range=(1, 2), max_features=100)),
        ('regressor', ExtraTreesRegressor(n_estimators=50, random_state=42))
    ])
    delay_pipeline.fit(X, y_delai)

    # 4. Sauvegarde des modèles dans le projet
    path_cost = os.path.join("app", "services", "ml", "cout", "cost_model.pkl")
    path_delay = os.path.join("app", "services", "ml", "delai", "delay_model.pkl")

    os.makedirs(os.path.dirname(path_cost), exist_ok=True)
    os.makedirs(os.path.dirname(path_delay), exist_ok=True)

    with open(path_cost, "wb") as f:
        pickle.dump(cost_pipeline, f)

    with open(path_delay, "wb") as f:
        pickle.dump(delay_pipeline, f)

    print(f"✅ Modèle COÛT enregistré : {path_cost}")
    print(f"✅ Modèle DÉLAI enregistré : {path_delay}")


if __name__ == "__main__":
    entrainer_et_sauvegarder()
    