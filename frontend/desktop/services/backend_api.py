import requests


class BackendAPI:

    BASE_URL = "http://127.0.0.1:8000"


    @classmethod
    def create_scan_session(cls):

        response = requests.post(
            f"{cls.BASE_URL}/scan/session"
        )

        response.raise_for_status()

        return response.json()


    @classmethod
    def get_session_status(cls, session_id):

        response = requests.get(
            f"{cls.BASE_URL}/scan/session/{session_id}"
        )

        response.raise_for_status()

        return response.json()


    @classmethod
    def close_session(cls, session_id):

        response = requests.delete(
            f"{cls.BASE_URL}/scan/session/{session_id}"
        )

        response.raise_for_status()

        return response.json()