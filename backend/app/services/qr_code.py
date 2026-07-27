import os
import socket
import qrcode


DOSSIER_QR = "uploads/qrcodes"

PORT_FRONTEND = 3000


def obtenir_ip_locale():

    try:

        # Connexion UDP virtuelle pour déterminer
        # l'interface réseau réellement utilisée
        socket_connexion = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        socket_connexion.connect(
            ("8.8.8.8", 80)
        )

        ip_locale = socket_connexion.getsockname()[0]

        socket_connexion.close()

        return ip_locale

    except Exception:

        return "127.0.0.1"


def generer_qr_code(

    numero_dossier: str

):

    os.makedirs(

        DOSSIER_QR,

        exist_ok=True

    )


    # Détection automatique de l'adresse IP
    ip_pc = obtenir_ip_locale()


    url = (

        f"http://{ip_pc}:{PORT_FRONTEND}"

        f"/reparation.html"

        f"?numero={numero_dossier}"

    )


    print(

        f"QR Code généré avec l'adresse : {url}"

    )


    chemin = os.path.join(

        DOSSIER_QR,

        f"{numero_dossier}.png"

    )


    image = qrcode.make(url)


    image.save(

        chemin

    )


    return chemin