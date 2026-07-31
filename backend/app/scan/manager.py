from .session import ScanSession


class ScanManager:

    def __init__(self):

        self.sessions = {}

    def create_session(self):

        session = ScanSession()

        self.sessions[session.session_id] = session

        return session

    def get(self, session_id):

        return self.sessions.get(session_id)

    def close(self, session_id):

        session = self.sessions.get(session_id)

        if session:

            session.closed = True

            return True

        return False

    def connect_phone(self, session_id):

        session = self.sessions.get(session_id)

        if session:

            session.connected = True

    def disconnect_phone(self, session_id):

        session = self.sessions.get(session_id)

        if session:

            session.connected = False


manager = ScanManager()