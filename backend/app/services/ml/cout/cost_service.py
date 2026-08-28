from app.services.ml.cout.cost_predictor import CostPredictor


_predictor = None


def get_cost_predictor():

    global _predictor

    if _predictor is None:

        _predictor = CostPredictor()

    return _predictor


def predict_cost(
    materiel,
    probleme
):

    predictor = get_cost_predictor()

    return predictor.predict(
        materiel=materiel,
        probleme=probleme
    )
