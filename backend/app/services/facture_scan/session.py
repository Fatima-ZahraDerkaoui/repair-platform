from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class ScanSession:

    session_id: str

    client_ip: str

    mobile_connected: bool = False

    created_at: datetime = field(default_factory=datetime.now)

    last_activity: datetime = field(default_factory=datetime.now)

    status: str = "WAITING"

    images: List[str] = field(default_factory=list)

    current_image: Optional[str] = None

    ocr_running: bool = False

    documents_processed: int = 0

    is_closed: bool = False

    def touch(self):

        self.last_activity = datetime.now()