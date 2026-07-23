import os

import qrcode


DOSSIER_QR = "uploads/qrcodes"

IP_PC = "192.168.1.16"
#IP_PC= "192.168.11.118"

PORT_FRONTEND = 3000


def generer_qr_code(

    numero_dossier: str

):

    os.makedirs(

        DOSSIER_QR,

        exist_ok=True

    )


    url = (

        f"http://{IP_PC}:{PORT_FRONTEND}"

        f"/reparation.html"

        f"?numero={numero_dossier}"

    )


    chemin = os.path.join(

        DOSSIER_QR,

        f"{numero_dossier}.png"

    )


    image = qrcode.make(url)

    image.save(chemin)


    return chemin