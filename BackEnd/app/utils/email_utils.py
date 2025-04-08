import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config_email import config_email

def enviar_email(destinatario, assunto, corpo):
    msg = MIMEMultipart()
    msg['From'] = config_email.EMAIL_REMETENTE
    msg['To'] = destinatario
    msg['Subject'] = assunto

    msg.attach(MIMEText(corpo, 'plain'))

    try:
        with smtplib.SMTP(config_email.EMAIL_SERVIDOR, config_email.EMAIL_PORTA) as servidor:
            servidor.starttls()
            servidor.login(config_email.EMAIL_REMETENTE, config_email.EMAIL_SENHA)
            servidor.send_message(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False
