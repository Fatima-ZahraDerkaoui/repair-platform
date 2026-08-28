from app.services.ml.cout.cost_predictor import CostPredictor


predictor = CostPredictor()


tests = [
    ("PC PORT HP", "BATTERIE"),
    ("IMPRIMANTE BROTHER", "DRUM"),
    ("PC PORT HP", "AFFICHEUR"),
    ("UNITE CENTRAL", "CARTE MERE"),
    ("PC PORT ASUS", "CHARGEUR"),
    ("MATERIEL INCONNU", "PROBLEME INCONNU"),
]


for materiel, probleme in tests:

    result = predictor.predict(
        materiel,
        probleme
    )

    print("\n------------------------------")
    print(f"Matériel : {materiel}")
    print(f"Problème : {probleme}")
    print(f"Coût estimé : {result['cout_estime']} DH")
    print(f"Confiance : {result['confiance']}")
    print(f"Historique : {result['historique']}")
    print(f"Source : {result['source']}")
