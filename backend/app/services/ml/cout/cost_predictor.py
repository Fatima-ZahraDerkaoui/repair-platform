from pathlib import Path
import re
import unicodedata

import joblib
import pandas as pd


# =========================================================
# CHEMINS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "cost_model.pkl"
HISTORY_PATH = BASE_DIR / "cost_history.pkl"


class CostPredictor:

    def __init__(self):

        # -------------------------------------------------
        # Chargement du modèle
        # -------------------------------------------------

        self.model = self._load(MODEL_PATH)

        # -------------------------------------------------
        # Chargement historique
        # -------------------------------------------------

        self.metadata = self._load(HISTORY_PATH)

        if not isinstance(self.metadata, dict):
            raise ValueError(
                "Le fichier cost_history.pkl est invalide."
            )

        if "history" not in self.metadata:
            raise ValueError(
                "La clé 'history' est absente."
            )

        self.history = self.metadata["history"]

        # -------------------------------------------------
        # Statistiques globales
        # -------------------------------------------------

        self.global_median = float(
            self.metadata.get(
                "global_median",
                200.0
            )
        )

        self.global_mean = float(
            self.metadata.get(
                "global_mean",
                self.global_median
            )
        )

    # =========================================================
    # CHARGEMENT
    # =========================================================

    @staticmethod
    def _load(path: Path):

        if not path.exists():

            raise FileNotFoundError(
                f"Fichier introuvable : {path}"
            )

        return joblib.load(path)

    # =========================================================
    # NORMALISATION
    # =========================================================

    @staticmethod
    def normalize_text(value):

        if value is None:
            return ""

        if pd.isna(value):
            return ""

        value = str(value).strip().upper()

        # Suppression accents
        value = unicodedata.normalize(
            "NFD",
            value
        )

        value = "".join(
            char
            for char in value
            if unicodedata.category(char) != "Mn"
        )

        # Espaces multiples
        value = re.sub(
            r"\s+",
            " ",
            value
        )

        # Corrections OCR fréquentes
        replacements = {

            "IPRIMANTE":
                "IMPRIMANTE",

            "IMPRIMANT":
                "IMPRIMANTE",

            "IMLPRIMANTE":
                "IMPRIMANTE",

            "CHAGEUR":
                "CHARGEUR",

            "CHARG":
                "CHARGEUR",

            "DROM":
                "DRUM",

            "DROUM":
                "DRUM",

            "BIOSS":
                "BIOS",

            "ISTALLATION OFFICE":
                "INSTALLATION OFFICE",
        }

        for old, new in replacements.items():

            value = value.replace(
                old,
                new
            )

        return value

    # =========================================================
    # NORMALISATION HISTORIQUE
    # =========================================================

    def _prepare_history(self):

        if self.history is None:
            return pd.DataFrame()

        if self.history.empty:
            return pd.DataFrame()

        history = self.history.copy()

        history["_materiel"] = (
            history["Matériel"]
            .fillna("")
            .apply(self.normalize_text)
        )

        history["_probleme"] = (
            history["Problème"]
            .fillna("")
            .apply(self.normalize_text)
        )

        return history

    # =========================================================
    # HISTORIQUE EXACT
    # =========================================================

    def _find_history(
        self,
        materiel,
        probleme
    ):

        history = self._prepare_history()

        if history.empty:
            return None

        materiel = self.normalize_text(
            materiel
        )

        probleme = self.normalize_text(
            probleme
        )

        result = history[
            (history["_materiel"] == materiel)
            &
            (history["_probleme"] == probleme)
        ]

        if result.empty:
            return None

        row = result.iloc[0]

        return {

            "count": int(
                row.get("count", 0)
            ),

            "valid_count": int(
                row.get(
                    "valid_count",
                    row.get("count", 0)
                )
            ),

            "zero_count": int(
                row.get(
                    "zero_count",
                    0
                )
            ),

            "median": float(
                row.get(
                    "median",
                    self.global_median
                )
            ),

            "mean": float(
                row.get(
                    "mean",
                    self.global_mean
                )
            ),

            "minimum": float(
                row.get(
                    "minimum",
                    0
                )
            ),

            "maximum": float(
                row.get(
                    "maximum",
                    0
                )
            ),
        }

    # =========================================================
    # HISTORIQUE PAR PROBLEME
    # =========================================================

    def _find_problem_history(
        self,
        probleme
    ):

        history = self._prepare_history()

        if history.empty:
            return None

        probleme = self.normalize_text(
            probleme
        )

        if not probleme:
            return None

        result = history[
            history["_probleme"] == probleme
        ]

        if result.empty:
            return None

        # -------------------------------------------------
        # On utilise la médiane de toutes les combinaisons
        # ayant le même problème.
        #
        # Pondération par le nombre d'occurrences.
        # -------------------------------------------------

        rows = []

        for _, row in result.iterrows():

            median = float(
                row.get(
                    "median",
                    0
                )
            )

            count = int(
                row.get(
                    "valid_count",
                    row.get(
                        "count",
                        0
                    )
                )
            )

            if count > 0:

                rows.extend(
                    [median] * count
                )

        if not rows:
            return None

        return {

            "prediction":
                float(
                    pd.Series(rows).median()
                ),

            "count":
                len(rows),
        }

    # =========================================================
    # HISTORIQUE PAR MATERIEL
    # =========================================================

    def _find_material_history(
        self,
        materiel
    ):

        history = self._prepare_history()

        if history.empty:
            return None

        materiel = self.normalize_text(
            materiel
        )

        if not materiel:
            return None

        result = history[
            history["_materiel"] == materiel
        ]

        if result.empty:
            return None

        rows = []

        for _, row in result.iterrows():

            median = float(
                row.get(
                    "median",
                    0
                )
            )

            count = int(
                row.get(
                    "valid_count",
                    row.get(
                        "count",
                        0
                    )
                )
            )

            if count > 0:

                rows.extend(
                    [median] * count
                )

        if not rows:
            return None

        return {

            "prediction":
                float(
                    pd.Series(rows).median()
                ),

            "count":
                len(rows),
        }

    # =========================================================
    # PRÉDICTION ML
    # =========================================================

    def _predict_ml(
        self,
        materiel,
        probleme
    ):

        input_data = pd.DataFrame([
            {
                "Matériel":
                    self.normalize_text(
                        materiel
                    ),

                "Problème":
                    self.normalize_text(
                        probleme
                    ),
            }
        ])

        try:

            prediction = self.model.predict(
                input_data
            )

            prediction = float(
                prediction[0]
            )

            prediction = max(
                0.0,
                prediction
            )

            return round(
                prediction,
                2
            )

        except Exception as e:

            raise RuntimeError(
                f"Impossible d'utiliser le modèle ML : {e}"
            )

    # =========================================================
    # PRÉDICTION PRINCIPALE
    # =========================================================

    def predict(
        self,
        materiel,
        probleme
    ):

        materiel = self.normalize_text(
            materiel
        )

        probleme = self.normalize_text(
            probleme
        )

        # =====================================================
        # 1. HISTORIQUE EXACT
        # =====================================================

        exact = self._find_history(
            materiel,
            probleme
        )

        if exact is not None:

            valid_count = exact[
                "valid_count"
            ]

            if valid_count > 0:

                if valid_count >= 5:

                    confidence = "Élevée"

                elif valid_count >= 2:

                    confidence = "Moyenne"

                else:

                    confidence = "Faible"

                return {

                    "cout_estime":
                        round(
                            exact["median"],
                            2
                        ),

                    "confiance":
                        confidence,

                    "historique":
                        exact["count"],

                    "historique_valide":
                        valid_count,

                    "montants_zero":
                        exact["zero_count"],

                    "source":
                        "historique_exact",
                }

        # =====================================================
        # 2. HISTORIQUE DU PROBLEME
        # =====================================================

        problem_history = (
            self._find_problem_history(
                probleme
            )
        )

        if problem_history is not None:

            count = problem_history[
                "count"
            ]

            if count >= 5:

                confidence = "Moyenne"

            else:

                confidence = "Faible"

            return {

                "cout_estime":
                    round(
                        problem_history[
                            "prediction"
                        ],
                        2
                    ),

                "confiance":
                    confidence,

                "historique":
                    count,

                "historique_valide":
                    count,

                "montants_zero":
                    0,

                "source":
                    "historique_probleme",
            }

        # =====================================================
        # 3. HISTORIQUE DU MATERIEL
        # =====================================================

        material_history = (
            self._find_material_history(
                materiel
            )
        )

        if material_history is not None:

            count = material_history[
                "count"
            ]

            if count >= 5:

                confidence = "Moyenne"

            else:

                confidence = "Faible"

            return {

                "cout_estime":
                    round(
                        material_history[
                            "prediction"
                        ],
                        2
                    ),

                "confiance":
                    confidence,

                "historique":
                    count,

                "historique_valide":
                    count,

                "montants_zero":
                    0,

                "source":
                    "historique_materiel",
            }

        # =====================================================
        # 4. MODELE ML
        # =====================================================

        prediction = self._predict_ml(
            materiel,
            probleme
        )

        return {

            "cout_estime":
                round(
                    prediction,
                    2
                ),

            "confiance":
                "Faible",

            "historique":
                0,

            "historique_valide":
                0,

            "montants_zero":
                0,

            "source":
                "modele_ml",
        }

    def _build_interval(self, prediction):

        minimum = max(
            self.global_median,
            prediction * 0.75
        )

        maximum = min(
            self.metadata.get(
                "global_maximum",
                1200
            ),
            prediction * 1.35
        )

        return (
            round(minimum, 2),
            round(maximum, 2)
        )
