import os
from twilio.rest import Client

class WhatsAppService:
    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.from_number = os.getenv('TWILIO_WHATSAPP_FROM', f"whatsapp:{os.getenv('TWILIO_PHONE_NUMBER')}")
    
    def send_message(self, to_number, message):
        """Send a WhatsApp message to the supervisor"""
        # Ensure the to_number has whatsapp: prefix and + sign
        # Remove any existing whatsapp: prefix first
        clean_number = to_number.replace("whatsapp:", "").strip()
        
        # Ensure it starts with +
        if not clean_number.startswith("+"):
            clean_number = f"+{clean_number}"
        
        to_number = f"whatsapp:{clean_number}"
        
        message = self.client.messages.create(
            from_=self.from_number,
            body=message,
            to=to_number
        )
        
        return message.sid
