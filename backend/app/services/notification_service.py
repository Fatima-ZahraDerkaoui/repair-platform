import requests


class NotificationService:

    def __init__(self):
        # 1. WhatsApp via GREEN-API
        self.wa_id_instance = "410022723230"
        self.wa_api_token = "8abb8fc4f44247c6a51d3a9d1afff7a72041a8b0fa4c470098"

        # 2. Telegram via Bot Father (Gratuit & Illimité)
        self.telegram_bot_token = "8528286893:AAHsp0nn-aoqz2b1pOhjF8wrcP-9lGfcfFo"

    def formater_numero_wa(self, telephone: str) -> str:
        """Nettoie le numéro au format international Maroc (2126... @c.us)."""
        tel = "".join(filter(str.isdigit, str(telephone)))
        if tel.startswith("0") and len(tel) == 10:
            tel = "212" + tel[1:]
        elif not tel.startswith("212"):
            tel = "212" + tel
        return f"{tel}@c.us"

    def envoyer_whatsapp(self, telephone: str, message: str) -> bool:
        """
        [MODE TEST] WHATSAPP DESACTIVE
        Retourne False pour simuler un quota dépassé ou une erreur.
        """
        print("[TEST] WhatsApp désactivé intentionnellement pour tester Telegram.")
        return False  # Force le basculement vers Telegram

    def envoyer_telegram(self, telegram_chat_id: str, message: str) -> bool:
        """Envoie le message via Telegram (Gratuit & Illimité)."""
        if not telegram_chat_id:
            print("[TELEGRAM ERREUR] Aucun Chat ID fourni.")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"

            payload = {
                "chat_id": telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown",
            }

            response = requests.post(url, json=payload, timeout=5)

            if response.status_code == 200:
                print(
                    f"[TELEGRAM SUCCÈS] Notification envoyée sur Telegram au Chat ID : {telegram_chat_id}"
                )
                return True
            else:
                print(
                    f"[TELEGRAM ERREUR] Code {response.status_code} - {response.text}"
                )
                return False

        except Exception as error:
            print(f"[TELEGRAM ERREUR] Échec de connexion : {error}")
            return False

    def notifier_client(
        self,
        nom_client: str,
        telephone: str,
        nom_machine: str,
        numero_dossier: str = None,
        telegram_chat_id: str = None,
    ):
        """Tente WhatsApp d'abord, puis bascule automatiquement sur Telegram."""
        dossier_info = (
            f"\n📄 *Dossier N° :* {numero_dossier}" if numero_dossier else ""
        )

        message = (
            f"🛠️ *DAY MACHINES — Service Technique*\n"
            f"─────────────────────────────\n\n"
            f"Bonjour *{nom_client}*,\n\n"
            f"Nous avons le plaisir de vous informer que la réparation de votre équipement est **TERMINÉE**.{dossier_info}\n"
            f"💻 *Matériel :* {nom_machine}\n\n"
            f"Votre appareil a été testé avec succès et est prêt à être récupéré à notre atelier.\n\n"
            f"📍 *Adresse :* Atelier Day Machines\n"
            f"⏰ *Horaires d'ouverture :*\n"
            f"   • Du Lundi au Vendredi : 09h00 - 18h00\n"
            f"   • Samedi : 09h00 - 15h00\n\n"
            f"Merci pour votre confiance !\n"
            f"— *L'équipe Day Machines*"
        )

        # 1. Tentative WhatsApp
        succes_wa = self.envoyer_whatsapp(telephone, message)

        # 2. Basculement automatique sur Telegram
        if not succes_wa and telegram_chat_id:
            print(
                "[INFO] WhatsApp non disponible : Basculement automatique sur Telegram..."
            )
            self.envoyer_telegram(telegram_chat_id, message)


# Instance globale réutilisée par FastAPI
notification_service = NotificationService()
