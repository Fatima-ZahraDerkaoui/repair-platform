import os

import qrcode


DOSSIER_QR = "uploads/qrcodes"


def generer_qr_code(numero_dossier: str):

    os.makedirs(DOSSIER_QR, exist_ok=True)

    chemin = os.path.join(
        DOSSIER_QR,
        f"{numero_dossier}.png"
    )

    image = qrcode.make(numero_dossier)

    image.save(chemin)

    return chemin