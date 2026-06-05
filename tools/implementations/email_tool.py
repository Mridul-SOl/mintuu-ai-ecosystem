import smtplib
from email.mime.text import MIMEText
import os
import logging
from typing import Dict, Any

logger = logging.getLogger("mintuu.tools.email")

class EmailTool:
    """Real SMTP email sending tool."""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        
    def execute(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        if not self.username or not self.password:
            logger.warning("SMTP credentials not configured. Simulating email send.")
            return {"status": "simulated", "to": to_email, "subject": subject}
            
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = to_email
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                
            return {"status": "success", "to": to_email}
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"error": str(e)}
