import os
import pickle
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def normaliser_texte(txt: str) -> str:
    """Nettoie le texte en supprimant les caractères spéciaux et les espaces superflus."""
    if pd.isna(txt):
        return ""
    txt = str(txt).upper().strip()
    txt = re.sub(r"[^A-Z0-9\s]", " ", txt)
    return " ".join(txt.split())


def evaluer_et_entrainer():
    # 1. Chargement des données
    data_path = os.path.join("data", "REPARATION.xlsx")
    if not os.path.exists(data_path):
        data_path = os.path.join("data", "REPARATION_clean.xlsx")

    print(f"📊 [ML EVAL] Chargement des données depuis : {data_path}")
    df = pd.read_excel(data_path)
    df.columns = [str(col).strip() for col in df.columns]

    # 2. Nettoyage des montants
    def parse_montant(val):
        if pd.isna(val):
            return 0.0
        val_str = (
            str(val).replace(" ", "").replace(",", ".").replace("DH", "")
        )
        try:
            return float(val_str)
        except ValueError:
            return 0.0

    df["Montant_Clean"] = df["Montant"].apply(parse_montant)

    # 3. Calcul propre du délai en jours (borné entre 0 et 30)
    df["Date Entrée"] = pd.to_datetime(df["Date Entrée"], errors="coerce")
    df["Date Sortie"] = pd.to_datetime(df["Date Sortie"], errors="coerce")
    df["Delai_Jours"] = (df["Date Sortie"] - df["Date Entrée"]).dt.days
    df["Delai_Jours"] = df["Delai_Jours"].apply(
        lambda x: int(x) if pd.notnull(x) and 0 <= x <= 30 else np.nan
    )

    # Imputation simple du délai manquant par la médiane
    mediane_delai = df["Delai_Jours"].median()
    df["Delai_Jours"] = df["Delai_Jours"].fillna(
        mediane_delai if pd.notna(mediane_delai) else 1.0
    )

    # 4. Filtrage des interventions réparées valides
    df_clean = df[
        (df["Réparé"].astype(str).str.upper().str.contains("OUI"))
        & (df["Montant_Clean"] > 0)
    ].copy()

    print(f"✅ [ML EVAL] Échantillons valides retenus : {len(df_clean)}\n")

    # Construction de la chaîne d'apprentissage
    df_clean["Feature_Text"] = (
        df_clean["Matériel"].apply(normaliser_texte)
        + " "
        + df_clean["Problème"].apply(normaliser_texte)
    )

    X = df_clean["Feature_Text"]
    y_cout = df_clean["Montant_Clean"]
    y_delai = df_clean["Delai_Jours"]

    # 5. Separation Train / Test (80% / 20%)
    X_tr_c, X_te_c, yc_tr, yc_te = train_test_split(
        X, y_cout, test_size=0.20, random_state=42
    )
    X_tr_d, X_te_d, yd_tr, yd_te = train_test_split(
        X, y_delai, test_size=0.20, random_state=42
    )

    # =========================================================
    # PIPELINE COÛT : Ridge Regression sur TF-IDF
    # =========================================================
    model_cost = Pipeline(
        [
            (
                "vectorizer",
                TfidfVectorizer(
                    ngram_range=(1, 2), min_df=2, sublinear_tf=True
                ),
            ),
            ("regressor", Ridge(alpha=1.0)),
        ]
    )

    model_cost.fit(X_tr_c, yc_tr)
    preds_c = model_cost.predict(X_te_c)

    r2_c = r2_score(yc_te, preds_c)
    rmse_c = np.sqrt(mean_squared_error(yc_te, preds_c))
    mae_c = mean_absolute_error(yc_te, preds_c)

    print("==================================================")
    print(" MÉTRIQUES D'ÉVALUATION : MODÈLE COÛT (DH)")
    print("==================================================")
    print(f"R² (R-squared) : {r2_c:.4f}")
    print(f"RMSE           : {rmse_c:.2f} DH")
    print(f"MAE            : {mae_c:.2f} DH")
    print("==================================================\n")

    # =========================================================
    # PIPELINE DÉLAI : Ridge Régularisé (alpha élevé)
    # =========================================================
    model_delay = Pipeline(
        [
            (
                "vectorizer",
                TfidfVectorizer(ngram_range=(1, 2), min_df=2),
            ),
            ("regressor", Ridge(alpha=10.0)),
        ]
    )

    model_delay.fit(X_tr_d, yd_tr)
    preds_d = model_delay.predict(X_te_d)

    r2_d = r2_score(yd_te, preds_d)
    rmse_d = np.sqrt(mean_squared_error(yd_te, preds_d))
    mae_d = mean_absolute_error(yd_te, preds_d)

    print("==================================================")
    print(" MÉTRIQUES D'ÉVALUATION : MODÈLE DÉLAI (JOURS)")
    print("==================================================")
    print(f"R² (R-squared) : {r2_d:.4f}")
    print(f"RMSE           : {rmse_d:.2f} Jours")
    print(f"MAE            : {mae_d:.2f} Jours")
    print("==================================================\n")

    # 6. Re-entraînement final sur tout le dataset et enregistrement
    model_cost.fit(X, y_cout)
    model_delay.fit(X, y_delai)

    path_cost = os.path.join("app", "services", "ml", "cout", "cost_model.pkl")
    path_delay = os.path.join(
        "app", "services", "ml", "delai", "delay_model.pkl"
    )

    os.makedirs(os.path.dirname(path_cost), exist_ok=True)
    os.makedirs(os.path.dirname(path_delay), exist_ok=True)

    with open(path_cost, "wb") as f:
        pickle.dump(model_cost, f)
    with open(path_delay, "wb") as f:
        pickle.dump(model_delay, f)

    print(f"✅ Modèle COÛT enregistré : {path_cost}")
    print(f"✅ Modèle DÉLAI enregistré : {path_delay}")


if __name__ == "__main__":
    evaluer_et_entrainer()