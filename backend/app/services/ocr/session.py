from dataclasses import dataclass
from pathlib import Path
import uuid


@dataclass
class ScanSession:

    id: str

    folder: Path

    status: str = "WAITING"

    document_type: str | None = None

    result: dict | None = None

    image_count: int = 0

    def add_image(self):

        self.image_count += 1