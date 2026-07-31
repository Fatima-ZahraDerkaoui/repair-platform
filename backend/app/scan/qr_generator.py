import socket
from pathlib import Path

import qrcode


UPLOAD_QR = Path("uploads/qrcodes")
UPLOAD_QR.mkdir(parents=True, exist_ok=True)


def get_local_ip():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:

        s.connect(("8.8.8.8", 80))

        ip = s.getsockname()[0]

    finally:

        s.close()

    return ip


def generate_qrcode(session_id: str):

    ip = get_local_ip()

    url = f"http://{ip}:8000/scan/mobile/{session_id}"

    filename = f"{session_id}.png"

    filepath = UPLOAD_QR / filename

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=2
    )

    qr.add_data(url)

    qr.make(fit=True)

    image = qr.make_image(fill_color="black",
                          back_color="white")

    image.save(filepath)

    return {

        "url": url,

        "path": str(filepath),

        "filename": filename

    }