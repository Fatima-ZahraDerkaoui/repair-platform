import requests


class WhatsAppService:

    def __init__(self):
        # ⚠️ REMPLACEZ AVEC VOS VRAIS IDENTIFIANTS GREEN-API
        self.id_instance = "VOTRE_ID_INSTANCE"
        self.api_token = "VOTRE_API_TOKEN"
        self.base_url = f"https://api.green-api.com/waInstance{self.id_instance}"

    def formater_numero(self, telephone: str) -> str:
        """Nettoie le numéro au format international Maroc (2126... @c.us)."""
        tel = "".join(filter(str.isdigit, str(telephone)))
        if tel.startswith("0") and len(tel) == 10:
            tel = "212" + tel[1:]
        elif not tel.startswith("212"):
            tel = "212" + tel
        return f"{tel}@c.us"

    def envoyer_notification_machine_terminee(
        self,
        telephone_client: str,
        nom_client: str,
        nom_machine: str
    ):
        """Envoie un vrai message WhatsApp sur le numéro de téléphone du client."""
        if not telephone_client:
            print("[WHATSAPP] Échec : Aucun numéro de téléphone fourni.")
            return False

        chat_id = self.formater_numero(telephone_client)
        url = f"{self.base_url}/sendMessage/{self.api_token}"

        message = (
            f"🛠️ *DAY MACHINES — Service Technique*\n"
            f"─────────────────────────────\n\n"
            f"Bonjour *{nom_client}*,\n\n"
            f"Nous avons le plaisir de vous informer que la réparation de votre équipement est **TERMINÉE**.\n"
            f"💻 *Matériel :* {nom_machine}\n\n"
            f"Votre appareil a été testé avec succès et est prêt à être récupéré à notre atelier.\n\n"
            f"📍 *Adresse :* Atelier Day Machines\n"
            f"⏰ *Horaires d'ouverture :* Du Lundi au Samedi (09h00 - 19h00)\n\n"
            f"Merci pour votre confiance !\n"
            f"— *L'équipe Day Machines*"
        )

        payload = {
            "chatId": chat_id,
            "message": message
        }

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                print(
                    f"[WHATSAPP REEL SUCCÈS] Message envoyé avec succès à {telephone_client} ({chat_id})"
                )
                return True
            else:
                print(
                    f"[WHATSAPP ERREUR] Code {response.status_code} - {response.text}"
                )
                return False

        except Exception as error:
            print(f"[WHATSAPP ERREUR] Échec de la connexion : {error}")
            return False


whatsapp_service = WhatsAppService()
