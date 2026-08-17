import requests
from pathlib import Path


class BackendAPI:

    BASE_URL = "http://127.0.0.1:8000"

    OCR_TIMEOUT = 300

    # =========================================================
    # OCR DIRECT
    # =========================================================

    @staticmethod
    def analyser_facture_direct(image_path):

        filename = Path(image_path).name

        with open(image_path, "rb") as f:

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
    # FACTURE SCAN - CREER SESSION
    # =========================================================

    @staticmethod
    def create_scan_session():

        response = requests.post(
            f"{BackendAPI.BASE_URL}/facture-scan/session",
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    # =========================================================
    # FACTURE SCAN - STATUT
    # =========================================================

    @staticmethod
    def get_session_status(session_id):

        response = requests.get(
            f"{BackendAPI.BASE_URL}/facture-scan/session/{session_id}",
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    # =========================================================
    # FACTURE SCAN - RESULTAT
    # =========================================================

    @staticmethod
    def get_facture_result(session_id):

        response = requests.get(
            f"{BackendAPI.BASE_URL}/facture-scan/result/{session_id}",
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    # =========================================================
    # FACTURE SCAN - FERMER SESSION
    # =========================================================

    @staticmethod
    def close_session(session_id):

        response = requests.delete(
            f"{BackendAPI.BASE_URL}/facture-scan/session/{session_id}",
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    # =========================================================
    # FACTURE SCAN - UPLOAD
    # =========================================================

    @staticmethod
    def upload_facture(
        session_id,
        image_path
    ):

        filename = Path(image_path).name

        with open(image_path, "rb") as f:

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

        return response.json()
    