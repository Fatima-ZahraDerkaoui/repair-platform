import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

def evaluer_modeles_ml():
    # 1. Chargement des données
    data_path = os.path.join("data", "REPARATION.xlsx")
    if not os.path.exists(data_path):
        data_path = os.path.join("data", "REPARATION_clean.xlsx")
        
    print(f"📊 [ML EVAL] Chargement des données depuis : {data_path}")
    df = pd.read_excel(data_path)

    # Nettoyage des colonnes
    df.columns = [str(col).strip() for col in df.columns]

    # Convertir et nettoyer les dates pour calculer le délai réel en jours
    df['Date Entrée'] = pd.to_datetime(df['Date Entrée'], errors='coerce')
    df['Date Sortie'] = pd.to_datetime(df['Date Sortie'], errors='coerce')
    df['Delai_Jours'] = (df['Date Sortie'] - df['Date Entrée']).dt.days
    df['Delai_Jours'] = df['Delai_Jours'].apply(lambda x: max(int(x), 1) if pd.notnull(x) and x >= 0 else 1)

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
    df['Matériel'] = df['Matériel'].fillna('Machine').astype(str)
    df['Problème'] = df['Problème'].fillna('Entretien').astype(str)

    # Filtrer uniquement les cas réparés valides avec montant > 0 pour l'évaluation
    df_clean = df[
        (df['Réparé'].astype(str).str.upper().str.contains('OUI')) & 
        (df['Montant_Clean'] > 0)
    ].copy()

    print(f"✅ [ML EVAL] Échantillons filtrés et valides : {len(df_clean)}\n")

    # Préparation des Features (X) et Targets (y)
    X = df_clean[['Matériel', 'Problème']]
    y_cout = df_clean['Montant_Clean']
    y_delai = df_clean['Delai_Jours']

    # Séparation Entraînement / Test (80% Train, 20% Test)
    X_train, X_test, y_cout_train, y_cout_test, y_delai_train, y_delai_test = train_test_split(
        X, y_cout, y_delai, test_size=0.20, random_state=42
    )

    # Pipeline de Preprocessing (One-Hot pour Matériel + TF-IDF pour Problème)
    preprocessor = ColumnTransformer(
        transformers=[
            ('materiel', OneHotEncoder(handle_unknown='ignore'), ['Matériel']),
            ('probleme', TfidfVectorizer(max_features=100), 'Problème')
        ]
    )

    # =========================================================
    # 2. ÉVALUATION DU MODÈLE DE COÛT (MONTANT DH)
    # =========================================================
    model_cost = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    model_cost.fit(X_train, y_cout_train)
    y_cout_pred = model_cost.predict(X_test)

    r2_cost = r2_score(y_cout_test, y_cout_pred)
    rmse_cost = np.sqrt(mean_squared_error(y_cout_test, y_cout_pred))
    mae_cost = mean_absolute_error(y_cout_test, y_cout_pred)

    print("==================================================")
    print(" 💰 MÉTRIQUES D'ÉVALUATION : MODÈLE COÛT (DH)")
    print("==================================================")
    print(f"   • R² (R-squared) : {r2_cost:.4f}")
    print(f"   • RMSE           : {rmse_cost:.2f} DH")
    print(f"   • MAE            : {mae_cost:.2f} DH")
    print("==================================================\n")

    # =========================================================
    # 3. ÉVALUATION DU MODÈLE DE DÉLAI (JOURS)
    # =========================================================
    model_delay = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    model_delay.fit(X_train, y_delai_train)
    y_delai_pred = model_delay.predict(X_test)

    r2_delay = r2_score(y_delai_test, y_delai_pred)
    rmse_delay = np.sqrt(mean_squared_error(y_delai_test, y_delai_pred))
    mae_delay = mean_absolute_error(y_delai_test, y_delai_pred)

    print("==================================================")
    print(" ⏱️ MÉTRIQUES D'ÉVALUATION : MODÈLE DÉLAI (JOURS)")
    print("==================================================")
    print(f"   • R² (R-squared) : {r2_delay:.4f}")
    print(f"   • RMSE           : {rmse_delay:.2f} Jours")
    print(f"   • MAE            : {mae_delay:.2f} Jours")
    print("==================================================\n")

if __name__ == "__main__":
    evaluer_modeles_ml()
    