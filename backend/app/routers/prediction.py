from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ml.cout.cost_predictor import CostPredictor
from app.services.ml.cout import cost_predictor
from app.services.ml.delai.delay_predictor import DelayPredictor

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)


# =========================================================
# CHARGEMENT UNIQUE DU MODÈLE
# =========================================================

predictor = CostPredictor()


# =========================================================
# REQUEST
# =========================================================

class CostPredictionRequest(BaseModel):
    materiel: str | None = None
    probleme: str | None = None


# =========================================================
# RESPONSE
# =========================================================

class CostPredictionResponse(BaseModel):
    cout_estime: float
    confiance: str
    historique: int
    historique_valide: int
    montants_zero: int
    source: str


# =========================================================
# PREDICTION
# =========================================================

@router.post(
    "/cout",
    response_model=CostPredictionResponse
)
def predict_cost_route(
    request: CostPredictionRequest
):
    try:

        result = predictor.predict(
            materiel=request.materiel or "",
            probleme=request.probleme or ""
        )

        return CostPredictionResponse(**result)

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction du coût : {error}"
        )

@router.get("/estimation-cout")
def estimer_cout_reparation(
    materiel: str,
    probleme: str
):
    """
    Endpoint pour interroger rapidement l'estimation depuis PySide6
    """
    res = cost_predictor.predict(
        materiel=materiel,
        probleme=probleme
    )
    return res


delay_predictor = DelayPredictor()

class DelayPredictionRequest(BaseModel):
    materiel: str | None = None
    probleme: str | None = None

@router.post("/delai")
def predict_delay_route(request: DelayPredictionRequest):
    try:
        delai_estime = delay_predictor.predict(
            materiel=request.materiel or "",
            probleme=request.probleme or ""
        )
        return {"delai_estime_jours": delai_estime}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Erreur prédiction délai: {error}")