import os
from twilio.rest import Client

class WhatsAppService:
    def __init__(self):
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        self.from_number = f"whatsapp:{os.getenv('TWILIO_PHONE_NUMBER')}"
    
    def send_message(self, to_number, message):
        """Send a WhatsApp message to the supervisor"""
        # Ensure the to_number has whatsapp: prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        message = self.client.messages.create(
            from_=self.from_number,
            body=message,
            to=to_number
        )
        
        return message.sid
