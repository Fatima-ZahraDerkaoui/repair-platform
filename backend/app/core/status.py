from enum import Enum


class StatutReparation(str, Enum):

    EN_ATTENTE = "En attente"

    DIAGNOSTIC = "Diagnostic"

    EN_REPARATION = "En réparation"

    EN_TEST = "En test"

    TERMINE = "Terminé"

    LIVRE = "Livré"

    ANNULE = "Annulé"