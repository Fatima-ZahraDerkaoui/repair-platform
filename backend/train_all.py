import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBRegressor
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials

# 1. Chargement et préparation des données
data_path = os.path.join("data", "data.xlsx")
df = pd.read_excel(data_path)

# Nettoyage du montant
if df['Montant (DH)'].dtype == object:
    df['Montant (DH)'] = (
        df['Montant (DH)']
        .astype(str)
        .str.replace(' ', '')
        .str.replace(',', '.')
        .astype(float)
    )

# Conversion des dates et calcul des délais
df['Date Entrée'] = pd.to_datetime(df['Date Entrée'], errors='coerce')
df['Date Sortie'] = pd.to_datetime(df['Date Sortie'], errors='coerce')
df['Delai_Jours'] = (df['Date Sortie'] - df['Date Entrée']).dt.days

# Conservation des réparations réussies
df_model = df[(df['Réparé'] == 'OUI') & (df['Delai_Jours'].notna()) & (df['Delai_Jours'] >= 0)].copy()

def categoriser_delai(j):
    return "Express (0-1j)" if j <= 1 else "Standard/Long (2j+)"

df_model['Delai_Classe'] = df_model['Delai_Jours'].apply(categoriser_delai)

# Features explicatives
feature_cols = [
    'Categorie_Materiel', 
    'Problème', 
    'Spec_Composant', 
    'Gamme_Piece', 
    'Type_Intervention', 
    'Quantite'
]

X = df_model[feature_cols]
num_features = ['Quantite']
cat_features = [c for c in feature_cols if c not in num_features]

preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(), num_features),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
])

# ==============================================================================
# 2. ENTRAÎNEMENT DU MODÈLE PRINCIPAL : COÛT (XGBoost)
# ==============================================================================
print("=== OPTIMISATION ET ENTRAÎNEMENT DU MODÈLE COÛT ===")

X_tr_c, X_te_c, y_tr_c, y_te_c = train_test_split(
    X, df_model['Montant (DH)'], test_size=0.2, random_state=42
)

X_tr_c_prep = preprocessor.fit_transform(X_tr_c)
X_te_c_prep = preprocessor.transform(X_te_c)

space = {
    'n_estimators': hp.quniform('n_estimators', 50, 300, 10),
    'max_depth': hp.choice('max_depth', range(3, 12)),
    'learning_rate': hp.loguniform('learning_rate', np.log(0.01), np.log(0.2)),
    'subsample': hp.uniform('subsample', 0.6, 1.0),
    'colsample_bytree': hp.uniform('colsample_bytree', 0.6, 1.0)
}

def objective(params):
    params['n_estimators'] = int(params['n_estimators'])
    model = XGBRegressor(**params, random_state=42)
    model.fit(X_tr_c_prep, y_tr_c)
    preds = model.predict(X_te_c_prep)
    return {'loss': mean_absolute_error(y_te_c, preds), 'status': STATUS_OK}

best_params = fmin(
    fn=objective,
    space=space,
    algo=tpe.suggest,
    max_evals=50,
    rstate=np.random.default_rng(42)
)

best_params['n_estimators'] = int(best_params['n_estimators'])
best_params['max_depth'] = int(best_params['max_depth'])

cost_pipeline = Pipeline([
    ('prep', preprocessor),
    ('reg', XGBRegressor(**best_params, random_state=42))
])
cost_pipeline.fit(X_tr_c, y_tr_c)

print(f"Performances Coût -> MAE: {mean_absolute_error(y_te_c, cost_pipeline.predict(X_te_c)):.2f} DH | R²: {r2_score(y_te_c, cost_pipeline.predict(X_te_c)):.4f}")

# ==============================================================================
# 3. ENTRAÎNEMENT DU MODÈLE SECONDAIRE : DÉLAI
# ==============================================================================
X_tr_d, X_te_d, y_tr_d, y_te_d = train_test_split(
    X, df_model['Delai_Classe'], test_size=0.2, random_state=42, stratify=df_model['Delai_Classe']
)

delay_pipeline = ImbPipeline([
    ('prep', preprocessor),
    ('smote', SMOTE(random_state=42, k_neighbors=2)),
    ('clf', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
])
delay_pipeline.fit(X_tr_d, y_tr_d)

# ==============================================================================
# 4. SAUVEGARDE SELON LA NOUVELLE ARBORESCENCE
# ==============================================================================
path_cost = os.path.join("backend", "app", "services", "ml", "cout", "cost_model.pkl")
path_delay = os.path.join("backend", "app", "services", "ml", "delai", "delay_model.pkl")

os.makedirs(os.path.dirname(path_cost), exist_ok=True)
os.makedirs(os.path.dirname(path_delay), exist_ok=True)

joblib.dump(cost_pipeline, path_cost)
joblib.dump(delay_pipeline, path_delay)

# Création automatique des dossiers s'ils n'existent pas
os.makedirs(os.path.dirname(path_cost), exist_ok=True)
os.makedirs(os.path.dirname(path_delay), exist_ok=True)

joblib.dump(cost_pipeline, path_cost)
joblib.dump(delay_pipeline, path_delay)

print(f"\n[OK] Sauvegarde effectuée avec succès :")
print(f"  • Modèle Coût  : {path_cost}")
print(f"  • Modèle Délai : {path_delay}")
