import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def enviar_email(destinatario: str, assunto: str, corpo: str):
    remetente = current_app.config['EMAIL_REMETENTE']
    senha = current_app.config['EMAIL_SENHA']
    servidor_smtp = current_app.config.get('EMAIL_SERVIDOR', 'smtp.gmail.com')
    porta = current_app.config.get('EMAIL_PORTA', 587)

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))

    try:
        servidor = smtplib.SMTP(servidor_smtp, porta)
        servidor.starttls()
        servidor.login(remetente, senha)
        servidor.sendmail(remetente, destinatario, msg.as_string())
        servidor.quit()
    except Exception as e:
        print(f"[EmailService] Erro ao enviar email: {e}")
