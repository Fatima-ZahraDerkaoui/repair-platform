from enum import Enum


class StatutReparation(str, Enum):

    EN_ATTENTE = "En attente"

    EN_DIAGNOSTIC = "En diagnostic"

    EN_REPARATION = "En réparation"

    TERMINE = "Terminé"
