import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings 

def send_status_notification(client_email: str, client_nom: str, numero_dossier: str, nouveau_statut: str):
    """
    Envoie un e-mail automatique au client lors du changement de statut du dossier.
    """
    subject = f"Suivi de réparation - Dossier {numero_dossier}"
    
    body = f"""
    Bonjour {client_nom},

    Le statut de votre équipement sous le dossier N° {numero_dossier} a été mis à jour.
    
    Nouveau statut : {nouveau_statut}

    Merci de votre confiance,
    L'équipe de maintenance.
    """

    # Configuration SMTP de secours si non configuré dans .env
    smtp_server = getattr(settings, "SMTP_SERVER", "smtp.gmail.com")
    smtp_port = getattr(settings, "SMTP_PORT", 587)
    sender_email = getattr(settings, "SENDER_EMAIL", "votre_email@gmail.com")
    sender_password = getattr(settings, "SENDER_PASSWORD", "votre_mot_de_passe_app")

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = client_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, client_email, msg.as_string())
        server.quit()
        print(f"[NOTIFICATION] Email envoyé avec succès à {client_email}")
        return True
    except Exception as e:
        print(f"[ERREUR NOTIFICATION] Impossible d'envoyer l'email : {e}")
        return False
    