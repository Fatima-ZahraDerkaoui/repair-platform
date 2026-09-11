import os
import pickle
import re
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def nettoyer_texte(txt) -> str:
    if pd.isna(txt) or not txt:
        return ""
    txt = str(txt).upper().strip()
    txt = re.sub(r"[^A-Z0-9\s]", " ", txt)
    return " ".join(txt.split())


def categoriser_prix(montant):
    """Définition des tranches de prix métiers."""
    if montant <= 200:
        return "1. Économique (< 200 DH)"
    elif montant <= 500:
        return "2. Moyen (200 - 500 DH)"
    else:
        return "3. Élevé (> 500 DH)"


def entrainer_classification():
    # 1. Chargement
    data_path = os.path.join("data", "REPARATION_v1.xlsx")
    if not os.path.exists(data_path):
        data_path = os.path.join("data", "REPARATION.xlsx")

    df = pd.read_excel(data_path)
    df.columns = [str(col).strip() for col in df.columns]

    def parse_montant(val):
        if pd.isna(val):
            return 0.0
        val_str = str(val).replace("\xa0", "").replace(" ", "").replace(",", ".").replace("DH", "")
        try:
            return float(val_str)
        except ValueError:
            return 0.0

    df["Montant_Clean"] = df["Montant"].apply(parse_montant)
    df_clean = df[(df["Réparé"].astype(str).str.upper().str.contains("OUI")) & (df["Montant_Clean"] > 0)].copy()

    df_clean["Feature_Text"] = (
        df_clean["Matériel"].apply(nettoyer_texte) + " " + df_clean["Problème"].apply(nettoyer_texte)
    )
    df_clean["Classe_Prix"] = df_clean["Montant_Clean"].apply(categoriser_prix)

    X = df_clean[["Feature_Text"]]
    y = df_clean["Classe_Prix"]

    # 2. Train / Test Split
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    # 3. Pipeline Classification
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "text",
                TfidfVectorizer(preprocessor=nettoyer_texte, ngram_range=(1, 2), min_df=1),
                "Feature_Text",
            )
        ]
    )

    clf_pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(n_estimators=150, random_state=42)),
        ]
    )

    clf_pipeline.fit(X_tr, y_tr)
    preds = clf_pipeline.predict(X_te)

    # 4. Évaluation
    acc = accuracy_score(y_te, preds)
    print("==================================================")
    print(f"🎯 ACCURACY MODÈLE CLASSIFICATION : {acc * 100:.2f} %")
    print("==================================================")
    print(classification_report(y_te, preds))

    # 5. Sauvegarde
    path_clf = os.path.join("app", "services", "ml", "cout", "cost_classifier_model.pkl")
    os.makedirs(os.path.dirname(path_clf), exist_ok=True)
    with open(path_clf, "wb") as f:
        pickle.dump(clf_pipeline, f)

    print(f"✅ Modèle de classification enregistré : {path_clf}")


if __name__ == "__main__":
    entrainer_classification()