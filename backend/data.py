import pandas as pd
import io

raw_data = """Ordre	Matériel	Date Entrée	Problème	Montant	Observation	Date Sortie	Réparé
[COLLER_VOTRE_TEXTE_ICI]"""

# Correction des sauts de ligne intempestifs et encodage
fixed_data = raw_data.replace('"ROULETTE\nDRUM"', 'ROULETTE / DRUM')
fixed_data = fixed_data.replace('dຜ.', 'déc.')

def parse_line(line):
    parts = line.split('\t')
    if len(parts) < 5:
        return None
    repare = parts[-1].strip() if parts[-1].strip() in ['OUI', 'NON'] else ''
    rest = parts[:-1] if repare else parts
    
    ordre = rest[0].strip() if len(rest) > 0 else ''
    materiel = rest[1].strip() if len(rest) > 1 else ''
    date_entree = rest[2].strip() if len(rest) > 2 else ''
    probleme = rest[3].strip() if len(rest) > 3 else ''
    montant = rest[4].strip() if len(rest) > 4 else ''
    
    rem_clean = [x.strip() for x in rest[5:] if x.strip() != '']
    observation, date_sortie = '', ''
    for x in rem_clean:
        if any(m in x.lower() for m in ['janv', 'févr', 'mars', 'avr', 'mai', 'juin', 'juil', 'août', 'sept', 'oct', 'nov', 'déc']):
            date_sortie = x
        else:
            observation = x
            
    return [ordre, materiel, date_entree, probleme, montant, observation, date_sortie, repare]

rows = [parse_line(line) for line in fixed_data.strip().split('\n')[1:] if parse_line(line) is not None]
df_clean = pd.DataFrame(rows, columns=['Ordre', 'Matériel', 'Date Entrée', 'Problème', 'Montant', 'Observation', 'Date Sortie', 'Réparé'])

# Exportation vers CSV / Excel
df_clean.to_csv('dataset_reparations_clean.csv', index=False, sep=';', encoding='utf-8-sig')
df_clean.to_excel('dataset_reparations_clean.xlsx', index=False)
print("Dataset de", len(df_clean), "lignes exporté avec succès.")