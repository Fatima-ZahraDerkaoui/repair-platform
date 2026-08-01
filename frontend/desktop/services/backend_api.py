import requests


class BackendAPI:

    BASE_URL = "http://127.0.0.1:8000"

    # ---------------------------------------------------------
    # FACTURE SCAN
    # ---------------------------------------------------------

    @staticmethod
    def create_scan_session():

        response = requests.post(
            f"{BackendAPI.BASE_URL}/facture-scan/session"
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------

    @staticmethod
    def get_session_status(session_id):

        response = requests.get(
            f"{BackendAPI.BASE_URL}/facture-scan/session/{session_id}"
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------

    @staticmethod
    def get_facture_result(session_id):

        response = requests.get(
            f"{BackendAPI.BASE_URL}/facture-scan/result/{session_id}"
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------

    @staticmethod
    def close_session(session_id):

        response = requests.delete(
            f"{BackendAPI.BASE_URL}/facture-scan/session/{session_id}"
        )

        response.raise_for_status()

        return response.json()

    # ---------------------------------------------------------

    @staticmethod
    def upload_facture(session_id, image_path):

        with open(image_path, "rb") as f:

            files = {
                "image": f
            }

            response = requests.post(
                f"{BackendAPI.BASE_URL}/facture-scan/upload/{session_id}",
                files=files
            )

        response.raise_for_status()

        return response.json()