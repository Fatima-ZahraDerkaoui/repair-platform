import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score, classification_report

# ==========================================
# 1. CHARGEMENT
# ==========================================
df = pd.read_excel('data/dataSet.xlsx')

APPLIQUER_CORRECTION = False

def corriger_prix_realiste(row):
    prob = str(row['Problème']).upper()
    montant = row['Montant (DH)']
    if 'AFFICHEUR' in prob and 0 < montant < 400:
        return 500
    elif 'DISQUE DUR' in prob and 0 < montant < 200:
        return 300
    elif 'CARTE MERE' in prob and 0 < montant < 300:
        return 400
    elif 'BATTERIE' in prob and 0 < montant < 150:
        return 250
    elif 'CLAVIER' in prob and 0 < montant < 250:
        return 350
    return montant

if APPLIQUER_CORRECTION:
    df['Montant_Corrige'] = df.apply(corriger_prix_realiste, axis=1)
else:
    df['Montant_Corrige'] = df['Montant (DH)']

# ==========================================
# 2. FEATURES (uniquement ce qu'on connaît AVANT la réparation)
# ==========================================
df['Date Entrée'] = pd.to_datetime(df['Date Entrée'])
df['Mois'] = df['Date Entrée'].dt.month
df['JourSemaine'] = df['Date Entrée'].dt.dayofweek

cat_cols = ['Matériel', 'Categorie_Materiel', 'Problème', 'Spec_Composant',
            'Gamme_Piece', 'Type_Intervention']
num_cols = ['Quantite', 'Mois', 'JourSemaine']
features = cat_cols + num_cols

def make_preprocessor():
    return ColumnTransformer([
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
        ('num', StandardScaler(), num_cols),
    ])

# ==========================================
# 3. MODÈLE DE COÛT
# ==========================================
df_payant = df[(df['Montant_Corrige'] > 0) & (df['Réparé'] == 'OUI')].copy()

X_tr, X_te, y_tr, y_te = train_test_split(
    df_payant[features], df_payant['Montant_Corrige'], test_size=0.2, random_state=42)

cost_pipeline = Pipeline([
    ('preprocessor', make_preprocessor()),
    ('regressor', GradientBoostingRegressor(
        n_estimators=400, learning_rate=0.02, max_depth=4, subsample=0.8, random_state=42)),
])
cost_pipeline.fit(X_tr, y_tr)
pred = cost_pipeline.predict(X_te)

print("--- MODÈLE DE COÛT ---")
print(f"Lignes utilisées : {len(df_payant)}")
print(f"MAE : {mean_absolute_error(y_te, pred):.2f} DH")
print(f"R²  : {r2_score(y_te, pred):.4f}\n")

# ==========================================
# 4. MODÈLES DE DÉLAI
# ==========================================
df['Delai_Binaire'] = (df['Delai_Jours'] > 0).astype(int)

# a) Classification
X_tr, X_te, y_tr, y_te = train_test_split(
    df[features], df['Delai_Binaire'], test_size=0.2, random_state=42, stratify=df['Delai_Binaire'])

delay_pipeline = Pipeline([
    ('preprocessor', make_preprocessor()),
    ('classifier', RandomForestClassifier(n_estimators=200, min_samples_leaf=3, random_state=42, n_jobs=-1)),
])
delay_pipeline.fit(X_tr, y_tr)
y_pred = delay_pipeline.predict(X_te)

print("--- MODÈLE DE DÉLAI (Classification) ---")
print(f"Accuracy : {accuracy_score(y_te, y_pred)*100:.2f}%")

# b) Régression (durée en jours)
X_tr, X_te, y_tr, y_te = train_test_split(
    df[features], df['Delai_Jours'], test_size=0.2, random_state=42)

delay_days_pipeline = Pipeline([
    ('preprocessor', make_preprocessor()),
    ('regressor', RandomForestRegressor(n_estimators=200, min_samples_leaf=3, random_state=42, n_jobs=-1)),
])
delay_days_pipeline.fit(X_tr, y_tr)
pred = delay_days_pipeline.predict(X_te)

print("--- MODÈLE DE DÉLAI (Régression : jours) ---")
print(f"MAE : {mean_absolute_error(y_te, pred):.2f} jours")
print(f"R²  : {r2_score(y_te, pred):.4f}\n")

# ==========================================
# 5. SAUVEGARDE PROPRE
# ==========================================
path_cost = os.path.join("app", "services", "ml", "cout", "cost_model.pkl")
path_delay = os.path.join("app", "services", "ml", "delai", "delay_model.pkl")
path_delay_days = os.path.join("app", "services", "ml", "delai", "delay_days_model.pkl")

os.makedirs(os.path.dirname(path_cost), exist_ok=True)
os.makedirs(os.path.dirname(path_delay), exist_ok=True)

joblib.dump(cost_pipeline, path_cost)
joblib.dump(delay_pipeline, path_delay)
joblib.dump(delay_days_pipeline, path_delay_days)

print("Modèles sauvegardés avec succès !")
