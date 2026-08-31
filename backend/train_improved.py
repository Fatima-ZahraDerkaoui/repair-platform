import os
import re
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline


def nettoyer_texte(texte: str) -> str:
    """Nettoie le texte et supprime le bruit."""
    if pd.isna(texte):
        return ""
    txt = str(texte).upper().strip()
    # Normalisation basique
    txt = re.sub(r'[^A-Z0-9\s]', ' ', txt)
    return " ".join(txt.split())


def entrainer_et_evaluer_ameliore():
    # 1. Chargement des données
    data_path = os.path.join("data", "REPARATION.xlsx")
    if not os.path.exists(data_path):
        data_path = os.path.join("data", "REPARATION_clean.xlsx")

    df = pd.read_excel(data_path)
    df.columns = [str(col).strip() for col in df.columns]

    # Nettoyage des dates
    df['Date Entrée'] = pd.to_datetime(df['Date Entrée'], errors='coerce')
    df['Date Sortie'] = pd.to_datetime(df['Date Sortie'], errors='coerce')

    # Calcul du délai (limité entre 1 et 15 jours pour éliminer les aberrations)
    df['Delai_Jours'] = (df['Date Sortie'] - df['Date Entrée']).dt.days
    df['Delai_Jours'] = df['Delai_Jours'].apply(
        lambda x: int(x) if pd.notnull(x) and 1 <= x <= 15 else 1
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

    # Filtrer uniquement les cas réparés valides
    df_clean = df[
        (df['Réparé'].astype(str).str.upper().str.contains('OUI')) &
        (df['Montant_Clean'] > 0)
    ].copy()

    # Feature Engineering : fusion propre du matériel et du problème
    df_clean['Texte_Complet'] = (
        df_clean['Matériel'].apply(nettoyer_texte) + " " +
        df_clean['Problème'].apply(nettoyer_texte)
    )

    X = df_clean['Texte_Complet']
    y_cout = df_clean['Montant_Clean']
    y_delai = df_clean['Delai_Jours']

    # Séparation Train / Test
    X_train, X_test, y_c_train, y_c_test, y_d_train, y_d_test = train_test_split(
        X, y_cout, y_delai, test_size=0.20, random_state=42
    )

    # =========================================================
    # 2. MODÈLE COÛT OPTIMISÉ (Gradient Boosting)
    # =========================================================
    model_cost = Pipeline(steps=[
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=150)),
        ('regressor', GradientBoostingRegressor(
            n_estimators=150, learning_rate=0.08, max_depth=4, random_state=42
        ))
    ])

    model_cost.fit(X_train, y_c_train)
    y_c_pred = model_cost.predict(X_test)

    print("\n==================================================")
    print(" 💰 MODÈLE COÛT AMÉLIORÉ (DH)")
    print("==================================================")
    print(f"   • R² (R-squared) : {r2_score(y_c_test, y_c_pred):.4f}")
    print(f"   • RMSE           : {np.sqrt(mean_squared_error(y_c_test, y_c_pred)):.2f} DH")
    print(f"   • MAE            : {mean_absolute_error(y_c_test, y_c_pred):.2f} DH")

    # =========================================================
    # 3. MODÈLE DÉLAI OPTIMISÉ
    # =========================================================
    model_delay = Pipeline(steps=[
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=100)),
        ('regressor', GradientBoostingRegressor(
            n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42
        ))
    ])

    model_delay.fit(X_train, y_d_train)
    y_d_pred = model_delay.predict(X_test)

    print("\n==================================================")
    print(" ⏱️ MODÈLE DÉLAI AMÉLIORÉ (JOURS)")
    print("==================================================")
    print(f"   • R² (R-squared) : {r2_score(y_d_test, y_d_pred):.4f}")
    print(f"   • RMSE           : {np.sqrt(mean_squared_error(y_d_test, y_d_pred)):.2f} Jours")
    print(f"   • MAE            : {mean_absolute_error(y_d_test, y_d_pred):.2f} Jours")
    print("==================================================\n")


if __name__ == "__main__":
    entrainer_et_evaluer_ameliore()
    