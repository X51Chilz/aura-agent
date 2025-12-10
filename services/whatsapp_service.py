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
        """Send a WhatsApp message to the supervisor (freeform - requires 24hr window)"""
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
    
    def send_template_message(self, to_number, template_name, variables):
        """Send a WhatsApp template message (for business-initiated messages)
        
        Args:
            to_number: Recipient WhatsApp number
            template_name: Name of approved template (e.g., 'email_notification')
            variables: List of variable values for template placeholders
        """
        # Ensure the to_number has whatsapp: prefix and + sign
        clean_number = to_number.replace("whatsapp:", "").strip()
        
        if not clean_number.startswith("+"):
            clean_number = f"+{clean_number}"
        
        to_number = f"whatsapp:{clean_number}"
        
        # Build content variables for template
        content_variables = {str(i+1): var for i, var in enumerate(variables)}
        
        message = self.client.messages.create(
            from_=self.from_number,
            to=to_number,
            content_sid=template_name,
            content_variables=content_variables
        )
        
        return message.sid
