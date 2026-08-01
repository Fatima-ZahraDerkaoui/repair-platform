import uuid
import socket
from datetime import datetime, timedelta
import json
from .session import ScanSession
from pathlib import Path
import shutil

class SessionManager:

    def __init__(self):

        self.sessions = {}

    # --------------------------

    def get_local_ip(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:

            s.connect(("8.8.8.8", 80))

            ip = s.getsockname()[0]

        finally:

            s.close()

        return ip

    # --------------------------

    def create_session(self):

        session_id = str(uuid.uuid4())

        folder = Path("uploads/temp") / session_id

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        session = ScanSession(

            session_id=session_id,

            client_ip=self.get_local_ip(),

            folder=folder

        )

        self.sessions[session_id] = session

        return session

    # --------------------------

    def get(self, session_id):

        return self.sessions.get(session_id)

    # --------------------------

    def connect_mobile(self, session_id):

        session = self.get(session_id)

        if session is None:
            return None

        session.mobile_connected = True

        session.status = "CONNECTED"

        session.touch()

        return session

    # --------------------------

    def disconnect_mobile(self, session_id):

        session = self.get(session_id)

        if session is None:
            return

        session.mobile_connected = False

        session.status = "WAITING"

        session.touch()

    # --------------------------

    def add_image(self, session_id, image_path):

        session = self.get(session_id)

        if session is None:
            return

        session.images.append(image_path)

        session.current_image = image_path

        session.status = "IMAGE_RECEIVED"

        session.touch()

    # --------------------------

    def start_ocr(self, session_id):

        session = self.get(session_id)

        if session is None:
            return

        session.ocr_running = True

        session.status = "OCR_RUNNING"

        session.touch()

    # --------------------------

    def finish_ocr(self, session_id):

        session = self.get(session_id)

        if session is None:
            return

        session.ocr_running = False

        session.documents_processed += 1

        session.status = "READY"

        session.touch()

    # --------------------------

    def close(self, session_id):

        session = self.get(session_id)

        if session is None:
            return

        if session.folder.exists():

            shutil.rmtree(
                session.folder,
                ignore_errors=True
            )

        session.is_closed = True

        session.status = "CLOSED"

        self.sessions.pop(
            session_id,
            None
        )
        
    # --------------------------

    def cleanup(self):

        now = datetime.now()

        expired = []

        for sid, session in self.sessions.items():

            if now - session.last_activity > timedelta(minutes=30):

                expired.append(sid)

        for sid in expired:

            self.sessions.pop(sid, None)


    def save_result(
            self,
            session_id: str,
            result: dict
    ):

        session = self.get(session_id)

        if session is None:
            return

        result_path = session.folder / "result.json"

        with open(
            result_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                result,
                f,
                ensure_ascii=False,
                indent=4
            )

        session.result = result

        session.document_type = result.get("document")

        session.status = "READY"

        session.touch()

    def get_result(
            self,
            session_id: str
    ):

        session = self.get(session_id)

        if session is None:
            return None

        return session.result

manager = SessionManager()