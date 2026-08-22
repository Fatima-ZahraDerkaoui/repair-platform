import requests
from pathlib import Path


class BackendAPI:

    BASE_URL = "http://127.0.0.1:8000"

    # OCR DIRECT
    OCR_TIMEOUT = 600

    # Requêtes rapides
    REQUEST_TIMEOUT = 15

    # Résultat session
    RESULT_TIMEOUT = 30

    # =========================================================
    # OCR DIRECT
    # =========================================================

    @staticmethod
    def analyser_facture_direct(image_path):

        filename = Path(
            image_path
        ).name

        with open(
            image_path,
            "rb"
        ) as f:

            files = {
                "fichier": (
                    filename,
                    f,
                    "application/octet-stream"
                )
            }

            response = requests.post(
                f"{BackendAPI.BASE_URL}/ocr/analyser",
                files=files,
                timeout=BackendAPI.OCR_TIMEOUT
            )

        response.raise_for_status()

        return response.json()

    # =========================================================
    # CREER SESSION
    # =========================================================

    @staticmethod
    def create_scan_session():

        response = requests.post(
            f"{BackendAPI.BASE_URL}/facture-scan/session",
            timeout=BackendAPI.REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    # =========================================================
    # STATUT SESSION
    # =========================================================

    @staticmethod
    def get_session_status(session_id):

        response = requests.get(
            f"{BackendAPI.BASE_URL}/facture-scan/session/{session_id}",
            timeout=BackendAPI.REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):

            raise ValueError(
                "Réponse statut session invalide."
            )

        return data

    # =========================================================
    # RESULTAT SESSION
    # =========================================================

    @staticmethod
    def get_facture_result(session_id):

        response = requests.get(
            f"{BackendAPI.BASE_URL}/facture-scan/result/{session_id}",
            timeout=BackendAPI.RESULT_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):

            raise ValueError(
                "Résultat OCR invalide."
            )

        return data

    # =========================================================
    # FERMER SESSION
    # =========================================================

    @staticmethod
    def close_session(session_id):

        try:

            response = requests.delete(
                f"{BackendAPI.BASE_URL}/facture-scan/session/{session_id}",
                timeout=BackendAPI.REQUEST_TIMEOUT
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:

            print(
                "[SCAN] Impossible de fermer la session :",
                e
            )

            return None

    # =========================================================
    # UPLOAD
    # =========================================================

    @staticmethod
    def upload_facture(
        session_id,
        image_path
    ):

        filename = Path(
            image_path
        ).name

        with open(
            image_path,
            "rb"
        ) as f:

            files = {
                "image": (
                    filename,
                    f,
                    "application/octet-stream"
                )
            }

            response = requests.post(
                f"{BackendAPI.BASE_URL}/facture-scan/upload/{session_id}",
                files=files,
                timeout=60
            )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):

            raise ValueError(
                "Réponse upload invalide."
            )

        return data

        # =========================================================
    
        # =========================================================
    
    # DASHBOARD - STATISTIQUES
    # =========================================================
    @staticmethod
    def get_dashboard_stats(periode="30j"):

        response = requests.get(
            f"{BackendAPI.BASE_URL}/dashboard/stats",
            params={
                "periode": periode
            },
            timeout=BackendAPI.REQUEST_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError(
                "Réponse statistiques dashboard invalide."
            )

        return data

    # ENREGISTRER FACTURE APRES VALIDATION
    # =========================================================

    @staticmethod
    def enregistrer_facture(data):

        if not isinstance(data, dict):

            raise ValueError(
                "Les données de facture sont invalides."
            )

        response = requests.post(
            f"{BackendAPI.BASE_URL}/factures",
            json=data,
            timeout=BackendAPI.REQUEST_TIMEOUT
        )

        response.raise_for_status()

        resultat = response.json()

        if not isinstance(resultat, dict):

            raise ValueError(
                "Réponse d'enregistrement invalide."
            )

        return resultat
    