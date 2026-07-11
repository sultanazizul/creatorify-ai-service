import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        self.host = os.environ.get("SMTP_HOST")
        self.port = int(os.environ.get("SMTP_PORT", 587))
        self.username = os.environ.get("SMTP_USERNAME")
        self.password = os.environ.get("SMTP_PASSWORD")
        self.from_email = os.environ.get("SMTP_FROM_EMAIL")

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False):
        if not all([self.host, self.username, self.password, self.from_email]):
            print("[EMAIL] Skipping email sending: Missing SMTP configuration.")
            print(f"[EMAIL] Host: {self.host}, User: {self.username}, From: {self.from_email}")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

            # Connect to server
            server = smtplib.SMTP(self.host, self.port)
            server.starttls() # Secure the connection
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            print(f"[EMAIL] Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"[EMAIL] Failed to send email to {to_email}: {e}")
            return False
