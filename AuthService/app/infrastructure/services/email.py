import smtplib
from email.message import EmailMessage

from domain.services.email import BaseEmailService


class SMTPEmailService(BaseEmailService):
    def __init__(self, smtp_server: str, smtp_port: int, smtp_address: str, smtp_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_address = smtp_address
        self.smtp_password = smtp_password
        
    def send_email(self, email: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg['From'] = self.smtp_address
        msg['To'] = email
        msg['Subject'] = subject
        msg.set_content(body, subtype='html')
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_address, self.smtp_password)
            server.send_message(msg)
        
        

        