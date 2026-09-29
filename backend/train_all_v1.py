import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# 1. Chargement et exclusion des montants à 0 DH (Piste 1)
df = pd.read_excel('data/data_nettoyee.xlsx')
df_payant = df[df['Montant (DH)'] > 0].copy()

# Feature Engineering temporel
df_payant['Date Entrée'] = pd.to_datetime(df_payant['Date Entrée'])
df_payant['Mois'] = df_payant['Date Entrée'].dt.month
df_payant['JourSemaine'] = df_payant['Date Entrée'].dt.dayofweek

features = [
    'Matériel', 'Categorie_Materiel', 'Problème', 'Spec_Composant', 
    'Gamme_Piece', 'Quantite', 'Type_Intervention', 'Réparé', 'Mois', 'JourSemaine'
]

X = df_payant[features]
y = df_payant['Montant (DH)']

cat_cols = ['Matériel', 'Categorie_Materiel', 'Problème', 'Spec_Composant', 'Gamme_Piece', 'Type_Intervention', 'Réparé']
num_cols = ['Quantite', 'Mois', 'JourSemaine']

preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols),
    ('num', StandardScaler(), num_cols)
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Utilisation d'un Gradient Boosting finement réglé (Piste 3)
model_ultime = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', GradientBoostingRegressor(
        n_estimators=400, 
        learning_rate=0.02, 
        max_depth=4, 
        subsample=0.8,
        random_state=42
    ))
])

model_ultime.fit(X_train, y_train)
y_pred = model_ultime.predict(X_test)

print("--- RÉSULTAT AVEC LES PISTES AVANCÉES ---")
print(f"MAE : {mean_absolute_error(y_test, y_pred):.2f} DH")
print(f"Score R² : {r2_score(y_test, y_pred):.4f}")
