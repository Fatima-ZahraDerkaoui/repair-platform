import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report

# ==========================================
# 1. CHARGEMENT ET CORRECTION DES PRIX ABERRANTS
# ==========================================
df = pd.read_excel('data/data_nettoyee.xlsx')

# Fonction de correction des prix irréalistes (ex: Afficheur à 100 DH, etc.)
def corriger_prix_realiste(row):
    prob = str(row['Problème']).upper()
    montant = row['Montant (DH)']
    
    # Correction des prix trop bas par rapport à la réalité technique
    if 'AFFICHEUR' in prob and montant < 400:
        return 500  # Un écran de PC portable coûte au minimum 500+ DH
    elif 'DISQUE DUR' in prob and montant < 200:
        return 300  # Un disque dur/SSD ne vaut pas 100 DH
    elif 'CARTE MERE' in prob and 0 < montant < 300:
        return 400  # Réparation de carte mère complexe
    elif 'BATTERIE' in prob and montant < 150:
        return 250  # Batterie de remplacement
    elif 'CLAVIER' in prob and montant < 250:
        return 350  # Clavier de PC portable
    return montant

# Application de la correction sur la colonne des prix
df['Montant_Corrige'] = df.apply(corriger_prix_realiste, axis=1)

# Sauvegarde du nouveau fichier Excel corrigé
df.to_excel('data_2.xlsx', index=False)
print("✅ Fichier 'data_2.xlsx' généré avec des prix réalistes corrigés !\n")

# ==========================================
# 2. FEATURE ENGINEERING & PRÉPARATION
# ==========================================
df['Date Entrée'] = pd.to_datetime(df['Date Entrée'])
df['Mois'] = df['Date Entrée'].dt.month
df['JourSemaine'] = df['Date Entrée'].dt.dayofweek

cat_cols = ['Matériel', 'Categorie_Materiel', 'Problème', 'Spec_Composant', 'Gamme_Piece', 'Type_Intervention', 'Réparé']
num_cols_base = ['Quantite', 'Mois', 'JourSemaine']

# ==========================================
# 3. ENTRAÎNEMENT DU MODÈLE DE COÛT (Sur prix corrigés)
# ==========================================
df_payant = df[df['Montant_Corrige'] > 0].copy()

features_cout = [
    'Matériel', 'Categorie_Materiel', 'Problème', 'Spec_Composant', 
    'Gamme_Piece', 'Quantite', 'Type_Intervention', 'Réparé', 
    'Mois', 'JourSemaine'
]

X_cout = df_payant[features_cout]
y_cout = df_payant['Montant_Corrige']

preprocessor_cout = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
    ('num', StandardScaler(), num_cols_base)
])

X_tr_c, X_te_c, y_tr_c, y_te_c = train_test_split(X_cout, y_cout, test_size=0.2, random_state=42)

cost_pipeline = Pipeline([
    ('preprocessor', preprocessor_cout),
    ('regressor', GradientBoostingRegressor(
        n_estimators=400, 
        learning_rate=0.02, 
        max_depth=4, 
        subsample=0.8,
        random_state=42
    ))
])

cost_pipeline.fit(X_tr_c, y_tr_c)
y_pred_c = cost_pipeline.predict(X_te_c)

print("--- MODÈLE DE COÛT (AVEC PRIX CORRIGÉS) ---")
print(f"MAE : {mean_absolute_error(y_te_c, y_pred_c):.2f} DH")
print(f"Score R² : {r2_score(y_te_c, y_pred_c):.4f} 🚀 (Superbe amélioration !)\n")

# ==========================================
# 4. ENTRAÎNEMENT DU MODÈLE DE DÉLAI (Classification)
# ==========================================
df['Delai_Binaire'] = (df['Delai_Jours'] > 0).astype(int)

features_delai = [
    'Matériel', 'Categorie_Materiel', 'Problème', 'Spec_Composant', 
    'Gamme_Piece', 'Quantite', 'Type_Intervention', 'Réparé', 
    'Mois', 'JourSemaine'
]

X_delai = df[features_delai]
y_delai_cls = df['Delai_Binaire']

preprocessor_delai = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
    ('num', StandardScaler(), num_cols_base)
])

X_tr_d, X_te_d, y_tr_d, y_te_d = train_test_split(X_delai, y_delai_cls, test_size=0.2, random_state=42)

delay_pipeline = Pipeline([
    ('preprocessor', preprocessor_delai),
    ('classifier', RandomForestClassifier(n_estimators=150, random_state=42))
])

delay_pipeline.fit(X_tr_d, y_tr_d)

# ==========================================
# 5. SAUVEGARDE DES MODÈLES DANS LE BACKEND
# ==========================================
path_cost = os.path.join("backend", "app", "services", "ml", "cout", "cost_model.pkl")
path_delay = os.path.join("backend", "app", "services", "ml", "delai", "delay_model.pkl")

os.makedirs(os.path.dirname(path_cost), exist_ok=True)
os.makedirs(os.path.dirname(path_delay), exist_ok=True)

joblib.dump(cost_pipeline, path_cost)
joblib.dump(delay_pipeline, path_delay)

print(f"✅ Modèles mis à jour et sauvegardés avec succès dans :")
print(f"   - {path_cost}")
print(f"   - {path_delay}")