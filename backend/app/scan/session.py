from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class ScanSession:

    session_id: str = field(default_factory=lambda: str(uuid4()))

    created_at: datetime = field(default_factory=datetime.now)

    connected: bool = False

    closed: bool = False

    current_document: str | None = None

    uploaded_files: list = field(default_factory=list)