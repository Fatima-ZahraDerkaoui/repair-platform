from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ml.cout.cost_predictor import CostPredictor

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)

# Initialisation unique du prédicteur (Coût + Délai)
predictor = CostPredictor()


# =========================================================
# SCHÉMAS PYDANTIC
# =========================================================

class PredictionRequest(BaseModel):
    materiel: str | None = None
    probleme: str | None = None


class CostPredictionResponse(BaseModel):
    cout_estime: float
    delai_estime: int
    confiance: str = "Élevée (Basée sur 809 réparations)"
    source: str = "Modèle Random Forest ML"


class DelayPredictionResponse(BaseModel):
    delai_estime_jours: int


# =========================================================
# ENDPOINTS
# =========================================================

@router.post("/cout", response_model=CostPredictionResponse)
def predict_cost_route(request: PredictionRequest):
    """
    Prédiction du coût et du délai estimé via POST (JSON)
    """
    try:
        res = predictor.predict(
            materiel=request.materiel or "",
            probleme=request.probleme or ""
        )
        return CostPredictionResponse(
            cout_estime=res["cout_estime"],
            delai_estime=res["delai_estime"]
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {error}"
        )


@router.get("/estimation-cout")
def estimer_cout_reparation(materiel: str = "", probleme: str = ""):
    """
    Endpoint GET direct pour la saisie rapide ou l'application PySide6
    Exemple: /prediction/estimation-cout?materiel=PC%20PORTABLE&probleme=AFFICHEUR
    """
    try:
        return predictor.predict(
            materiel=materiel,
            probleme=probleme
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur estimation rapide : {error}"
        )


@router.post("/delai", response_model=DelayPredictionResponse)
def predict_delay_route(request: PredictionRequest):
    """
    Prédiction ciblée sur le délai de réparation
    """
    try:
        res = predictor.predict(
            materiel=request.materiel or "",
            probleme=request.probleme or ""
        )
        return DelayPredictionResponse(
            delai_estime_jours=res["delai_estime"]
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur prédiction délai : {error}"
        )