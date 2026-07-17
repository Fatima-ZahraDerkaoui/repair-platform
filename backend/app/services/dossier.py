from datetime import datetime


def generer_numero_dossier(id_reparation: int) -> str:
    annee = datetime.now().year
    return f"REP-{annee}-{id_reparation:06d}"