from pathlib import Path
import joblib
import pandas as pd
import re
import unicodedata

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "delay_model.pkl"
HISTORY_PATH = BASE_DIR / "delay_history.pkl"

class DelayPredictor:
    def __init__(self):
        try:
            self.model = joblib.load(MODEL_PATH)
            self.metadata = joblib.load(HISTORY_PATH)
        except Exception:
            self.model = None
            self.metadata = {"global_median": 2.0}

    @staticmethod
    def normalize_text(value):
        if not value: return ""
        value = str(value).strip().upper()
        value = unicodedata.normalize("NFD", value)
        return "".join(c for c in value if unicodedata.category(c) != "Mn")

    def predict(self, materiel: str, probleme: str) -> float:
        if self.model:
            input_df = pd.DataFrame([{
                "Matériel": self.normalize_text(materiel),
                "Problème": self.normalize_text(probleme)
            }])
            delai = self.model.predict(input_df)[0]
            return max(1.0, round(float(delai), 1))
        
        return float(self.metadata.get("global_median", 2.0))
    