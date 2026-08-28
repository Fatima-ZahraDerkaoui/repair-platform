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
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# =========================================================
# CHEMINS
# =========================================================

# backend/
BASE_DIR = Path(__file__).resolve().parents[4]

# Dataset original
DATA_PATH = BASE_DIR / "data" / "REPARATION.xlsx"

# Dataset nettoyé
CLEAN_DATA_PATH = BASE_DIR / "data" / "REPARATION_clean.xlsx"

# Dossier courant :
# backend/app/services/ml/cout/
MODEL_DIR = Path(__file__).resolve().parent

MODEL_PATH = MODEL_DIR / "cost_model.pkl"
HISTORY_PATH = MODEL_DIR / "cost_history.pkl"


# =========================================================
# CONFIGURATION
# =========================================================

FEATURES = [
    "Matériel",
    "Problème",
]

TARGET = "Montant"

# Nombre minimum de valeurs positives nécessaires
# pour remplacer un montant égal à 0.
MIN_POSITIVE_VALUES_FOR_ZERO_REPLACEMENT = 2


# =========================================================
# NORMALISATION TEXTE
# =========================================================

def normalize_text(value):

    if pd.isna(value):
        return ""

    value = str(value).strip().upper()

    # Suppression des accents
    value = unicodedata.normalize(
        "NFD",
        value
    )

    value = "".join(
        char
        for char in value
        if unicodedata.category(char) != "Mn"
    )

    # Espaces multiples
    value = re.sub(
        r"\s+",
        " ",
        value
    )

    # Corrections simples
    replacements = {

        "IPRIMANTE": "IMPRIMANTE",
        "IMPRIMANT": "IMPRIMANTE",
        "IMLPRIMANTE": "IMPRIMANTE",

        "CHAGEUR": "CHARGEUR",
        "CHARG": "CHARGEUR",

        "DROM": "DRUM",
        "DROUM": "DRUM",

        "BIOSS": "BIOS",

        "ISTALLATION OFFICE":
            "INSTALLATION OFFICE",
    }

    for old, new in replacements.items():
        value = value.replace(
            old,
            new
        )

    return value


# =========================================================
# NETTOYAGE DU MONTANT
# =========================================================

def clean_amount(value):

    if pd.isna(value):
        return None

    if isinstance(value, (int, float)):

        return float(value)

    value = str(value)

    value = value.replace(
        "\xa0",
        ""
    )

    value = value.replace(
        " ",
        ""
    )

    value = value.replace(
        "DH",
        ""
    )

    value = value.replace(
        "MAD",
        ""
    )

    # Exemple :
    # 250,50 -> 250.50
    value = value.replace(
        ",",
        "."
    )

    try:

        return float(value)

    except (
        ValueError,
        TypeError
    ):

        return None


# =========================================================
# CHARGEMENT DATASET
# =========================================================

print(
    "Chargement du dataset..."
)

if not DATA_PATH.exists():

    raise FileNotFoundError(
        f"Dataset introuvable : {DATA_PATH}"
    )


df = pd.read_excel(
    DATA_PATH
)


print(
    f"Nombre de lignes : {len(df)}"
)


# =========================================================
# NETTOYAGE NOMS COLONNES
# =========================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)


print(
    "Colonnes détectées :"
)

print(
    df.columns.tolist()
)


# =========================================================
# VÉRIFICATION COLONNES
# =========================================================

required_columns = FEATURES + [
    TARGET
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    raise ValueError(
        "Colonnes manquantes : "
        + ", ".join(missing_columns)
    )


# =========================================================
# SÉLECTION
# =========================================================

df = df[
    FEATURES + [TARGET]
].copy()


# =========================================================
# NORMALISATION TEXTE
# =========================================================

for column in FEATURES:

    df[column] = df[column].apply(
        normalize_text
    )


# =========================================================
# NETTOYAGE MONTANT
# =========================================================

df[TARGET] = df[TARGET].apply(
    clean_amount
)


# =========================================================
# STATISTIQUES AVANT NETTOYAGE
# =========================================================

print(
    "\n=============================="
)

print(
    "AVANT DATA CLEANING"
)

print(
    "=============================="
)


null_count_before = int(
    df[TARGET].isna().sum()
)

zero_count_before = int(
    (df[TARGET] == 0).sum()
)

negative_count_before = int(
    (df[TARGET] < 0).sum()
)


print(
    f"Montants NULL : {null_count_before}"
)

print(
    f"Montants = 0  : {zero_count_before}"
)

print(
    f"Montants négatifs : {negative_count_before}"
)


# =========================================================
# SUPPRESSION MONTANTS INVALIDES
# =========================================================

df = df.dropna(
    subset=[TARGET]
).copy()


# =========================================================
# SUPPRESSION MONTANTS NÉGATIFS
# =========================================================

df = df[
    df[TARGET] >= 0
].copy()


# =========================================================
# SUPPRESSION LIGNES VIDES
# =========================================================

df = df[
    (df["Matériel"] != "")
    |
    (df["Problème"] != "")
].copy()


# =========================================================
# DATA CLEANING DES 0 DH
# =========================================================

print(
    "\n=============================="
)

print(
    "DATA CLEANING DES MONTANTS 0 DH"
)

print(
    "=============================="
)


zero_mask = (
    df[TARGET] == 0
)


zero_indices = df.index[
    zero_mask
]


replaced_zero_count = 0
kept_zero_count = 0


corrections = []


# ---------------------------------------------------------
# Pour chaque ligne avec montant = 0
# ---------------------------------------------------------

for index in zero_indices:

    materiel = df.at[
        index,
        "Matériel"
    ]

    probleme = df.at[
        index,
        "Problème"
    ]


    # Chercher les montants positifs
    # pour la même combinaison
    same_combination = df[
        (df["Matériel"] == materiel)
        &
        (df["Problème"] == probleme)
        &
        (df[TARGET] > 0)
    ]


    positive_values = (
        same_combination[TARGET]
        .dropna()
    )


    # -----------------------------------------------------
    # Remplacement si suffisamment de données
    # -----------------------------------------------------

    if len(
        positive_values
    ) >= MIN_POSITIVE_VALUES_FOR_ZERO_REPLACEMENT:

        old_value = 0.0

        replacement_value = float(
            positive_values.median()
        )


        df.at[
            index,
            TARGET
        ] = replacement_value


        replaced_zero_count += 1


        corrections.append({

            "index": int(index),

            "Matériel": materiel,

            "Problème": probleme,

            "ancien_montant": old_value,

            "nouveau_montant": replacement_value,

            "nombre_valeurs_positives":
                len(positive_values),

            "methode":
                "mediane_materiel_probleme",
        })


    else:

        kept_zero_count += 1


# =========================================================
# RÉSULTATS DATA CLEANING
# =========================================================

print(
    f"Montants 0 avant nettoyage : "
    f"{zero_count_before}"
)

print(
    f"Montants 0 remplacés : "
    f"{replaced_zero_count}"
)

print(
    f"Montants 0 conservés : "
    f"{kept_zero_count}"
)


# =========================================================
# AFFICHER LES PREMIÈRES CORRECTIONS
# =========================================================

if corrections:

    print(
        "\nPremières corrections :"
    )

    for correction in corrections[:20]:

        print(
            f"- "
            f"{correction['Matériel']} | "
            f"{correction['Problème']} | "
            f"0 DH -> "
            f"{correction['nouveau_montant']:.2f} DH "
            f"("
            f"{correction['nombre_valeurs_positives']} "
            f"valeurs positives"
            f")"
        )

else:

    print(
        "\nAucune valeur 0 n'a été remplacée."
    )


# =========================================================
# SAUVEGARDE DATASET NETTOYÉ
# =========================================================

try:

    df.to_excel(
        CLEAN_DATA_PATH,
        index=False
    )

    print(
        "\nDataset nettoyé sauvegardé :"
    )

    print(
        CLEAN_DATA_PATH
    )

except Exception as e:

    print(
        "\nAttention : impossible de sauvegarder "
        "REPARATION_clean.xlsx"
    )

    print(
        str(e)
    )


# =========================================================
# STATISTIQUES APRÈS CLEANING
# =========================================================

print(
    "\n=============================="
)

print(
    "APRÈS DATA CLEANING"
)

print(
    "=============================="
)


print(
    f"Nombre de lignes : {len(df)}"
)

print(
    f"Montants = 0 : "
    f"{int((df[TARGET] == 0).sum())}"
)

print(
    f"Montants positifs : "
    f"{int((df[TARGET] > 0).sum())}"
)

print(
    f"Montant minimum : "
    f"{df[TARGET].min():.2f} DH"
)

print(
    f"Montant maximum : "
    f"{df[TARGET].max():.2f} DH"
)


# =========================================================
# HISTORIQUE
# =========================================================

print(
    "\n=============================="
)

print(
    "CONSTRUCTION DE L'HISTORIQUE"
)

print(
    "=============================="
)


def calculate_history(group):

    amounts = group[TARGET]

    total_count = len(
        amounts
    )

    positive_amounts = amounts[
        amounts > 0
    ]


    # Après le data cleaning,
    # les valeurs positives sont prioritaires.
    if len(
        positive_amounts
    ) > 0:

        values = positive_amounts

    else:

        values = amounts


    return pd.Series({

        "count":
            total_count,

        "valid_count":
            len(values),

        "zero_count":
            int(
                (amounts == 0).sum()
            ),

        "median":
            float(
                values.median()
            ),

        "mean":
            float(
                values.mean()
            ),

        "minimum":
            float(
                values.min()
            ),

        "maximum":
            float(
                values.max()
            ),
    })


history = (
    df
    .groupby(
        FEATURES,
        group_keys=False
    )
    .apply(
        calculate_history
    )
    .reset_index()
)


print(
    f"Nombre de combinaisons : "
    f"{len(history)}"
)


# =========================================================
# STATISTIQUES GLOBALES
# =========================================================

global_median = float(
    df[TARGET].median()
)

global_mean = float(
    df[TARGET].mean()
)

global_min = float(
    df[TARGET].min()
)

global_max = float(
    df[TARGET].max()
)


print(
    f"Médiane globale : "
    f"{global_median:.2f} DH"
)

print(
    f"Moyenne globale : "
    f"{global_mean:.2f} DH"
)

print(
    f"Minimum global : "
    f"{global_min:.2f} DH"
)

print(
    f"Maximum global : "
    f"{global_max:.2f} DH"
)


# =========================================================
# DONNÉES ML
# =========================================================

X = df[
    FEATURES
].copy()

y = df[
    TARGET
].copy()


# =========================================================
# TRAIN / TEST
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.20,

    random_state=42,
)


print(
    "\n=============================="
)

print(
    "DONNÉES ML"
)

print(
    "=============================="
)

print(
    f"Données entraînement : "
    f"{len(X_train)}"
)

print(
    f"Données test : "
    f"{len(X_test)}"
)


# =========================================================
# PRÉTRAITEMENT
# =========================================================

preprocessor = ColumnTransformer(

    transformers=[

        (
            "categorical",

            Pipeline([

                (
                    "imputer",

                    SimpleImputer(
                        strategy="most_frequent"
                    ),
                ),

                (
                    "encoder",

                    OneHotEncoder(
                        handle_unknown="ignore"
                    ),
                ),
            ]),

            FEATURES,
        ),
    ],

    remainder="drop",
)


# =========================================================
# RANDOM FOREST
# =========================================================

model = RandomForestRegressor(

    n_estimators=300,

    max_depth=15,

    min_samples_leaf=2,

    random_state=42,

    n_jobs=-1,
)


# =========================================================
# PIPELINE
# =========================================================

pipeline = Pipeline([

    (
        "preprocessor",

        preprocessor,
    ),

    (
        "model",

        model,
    ),
])


# =========================================================
# ENTRAÎNEMENT
# =========================================================

print(
    "\nEntraînement du modèle ML..."
)


pipeline.fit(
    X_train,
    y_train,
)


# =========================================================
# ÉVALUATION
# =========================================================

predictions = pipeline.predict(
    X_test
)


mae = mean_absolute_error(
    y_test,
    predictions
)


rmse = mean_squared_error(
    y_test,
    predictions
) ** 0.5


r2 = r2_score(
    y_test,
    predictions
)


print(
    "\n=============================="
)

print(
    "RÉSULTATS DU MODÈLE ML"
)

print(
    "=============================="
)

print(
    f"MAE  : {mae:.2f} DH"
)

print(
    f"RMSE : {rmse:.2f} DH"
)

print(
    f"R²   : {r2:.4f}"
)


# =========================================================
# RÉENTRAÎNEMENT FINAL
# =========================================================

print(
    "\nRéentraînement final sur "
    "toutes les données nettoyées..."
)


pipeline.fit(
    X,
    y
)


# =========================================================
# MÉTADONNÉES
# =========================================================

metadata = {

    "history":
        history,

    "global_median":
        global_median,

    "global_mean":
        global_mean,

    "global_min":
        global_min,

    "global_max":
        global_max,

    "features":
        FEATURES,

    "target":
        TARGET,

    "n_samples":
        len(df),

    "mae":
        float(mae),

    "rmse":
        float(rmse),

    "r2":
        float(r2),

    "model_type":
        "RandomForestRegressor",

    "data_cleaning":
        {

            "zero_count_before":
                zero_count_before,

            "zero_replaced":
                replaced_zero_count,

            "zero_kept":
                kept_zero_count,

            "null_removed":
                null_count_before,

            "negative_removed":
                negative_count_before,

            "zero_replacement_method":
                "median_of_positive_values_by_"
                "materiel_and_probleme",

            "minimum_positive_values":
                MIN_POSITIVE_VALUES_FOR_ZERO_REPLACEMENT,
        },

    "corrections":
        corrections,
}


# =========================================================
# CRÉATION DOSSIER
# =========================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# SUPPRESSION ANCIENS FICHIERS
# =========================================================

if MODEL_PATH.exists():

    MODEL_PATH.unlink()


if HISTORY_PATH.exists():

    HISTORY_PATH.unlink()


# =========================================================
# SAUVEGARDE MODÈLE
# =========================================================

joblib.dump(
    pipeline,
    MODEL_PATH
)


# =========================================================
# SAUVEGARDE HISTORIQUE
# =========================================================

joblib.dump(
    metadata,
    HISTORY_PATH
)


# =========================================================
# FIN
# =========================================================

print(
    "\n=============================="
)

print(
    "SAUVEGARDE TERMINÉE"
)

print(
    "=============================="
)

print(
    f"Modèle : {MODEL_PATH}"
)

print(
    f"Historique : {HISTORY_PATH}"
)

print(
    f"Dataset nettoyé : {CLEAN_DATA_PATH}"
)

print(
    "\nEntraînement terminé avec succès."
)
