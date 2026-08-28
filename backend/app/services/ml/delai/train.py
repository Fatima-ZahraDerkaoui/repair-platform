from pathlib import Path
import re
import unicodedata
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = Path(__file__).resolve().parents[4]
DATA_PATH = BASE_DIR / "data" / "REPARATION.xlsx"
MODEL_DIR = Path(__file__).resolve().parent

MODEL_PATH = MODEL_DIR / "delay_model.pkl"
HISTORY_PATH = MODEL_DIR / "delay_history.pkl"

def normalize_text(value):
    if pd.isna(value): return ""
    value = str(value).strip().upper()
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", value)

print("Entraînement du modèle de prédiction des délais...")

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset introuvable : {DATA_PATH}")

df = pd.read_excel(DATA_PATH)
df.columns = df.columns.astype(str).str.strip()

# Calcul du délai en jours
df['Date Entrée'] = pd.to_datetime(df['Date Entrée'], errors='coerce')
df['Date Sortie'] = pd.to_datetime(df['Date Sortie'], errors='coerce')

# Filtrer les données valides
df = df.dropna(subset=['Date Entrée', 'Date Sortie']).copy()
df['Delai_Jours'] = (df['Date Sortie'] - df['Date Entrée']).dt.days

# Conserver uniquement les délais valides (>= 0 jours)
df = df[df['Delai_Jours'] >= 0].copy()

FEATURES = ["Matériel", "Problème"]
TARGET = "Delai_Jours"

for col in FEATURES:
    df[col] = df[col].apply(normalize_text)

X = df[FEATURES]
y = df[TARGET]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore"))
        ]), FEATURES)
    ]
)

model = RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42)
pipeline = Pipeline([("preprocessor", preprocessor), ("model", model)])

pipeline.fit(X, y)

# Sauvegarde
MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline, MODEL_PATH)

global_median = float(y.median())
metadata = {
    "global_median": global_median,
    "global_mean": float(y.mean()),
    "n_samples": len(df)
}
joblib.dump(metadata, HISTORY_PATH)

print(f"Modèle des délais sauvegardé dans : {MODEL_PATH}")
print(f"Délai médian global : {global_median:.1f} jour(s)")
