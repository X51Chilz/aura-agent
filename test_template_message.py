#!/usr/bin/env python3
"""Test WhatsApp template message"""
import os
import sys
sys.path.insert(0, '/home/peter/aura_agent')

from dotenv import load_dotenv
from services.whatsapp_service import WhatsAppService

load_dotenv('/home/peter/aura_agent/.env')

whatsapp = WhatsAppService()
supervisor = os.getenv("SUPERVISOR_WHATSAPP")
template_sid = os.getenv("WHATSAPP_TEMPLATE_SID")

print(f"Testing template message...")
print(f"Template SID: {template_sid}")
print(f"To: {supervisor}")
print()

try:
    # Send template message with test data
    message_sid = whatsapp.send_template_message(
        supervisor,
        template_sid,
        [
            "test@example.com",                    # {{1}} - sender
            "Test Email Subject",                  # {{2}} - subject
            "This is a test of Amy's template message system. If you receive this, the WhatsApp Business API template is working correctly!"  # {{3}} - summary
        ]
    )
    
    print(f"✅ Template message sent!")
    print(f"Message SID: {message_sid}")
    print()
    print("Check your WhatsApp - you should receive a message from +48732096794")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
