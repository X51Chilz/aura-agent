#!/usr/bin/env python3
"""
Helper script to check template approval status and get Content SID.
Run this after Twilio approves your template.
"""
import os
import sys
sys.path.insert(0, '/home/peter/aura_agent')

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv('/home/peter/aura_agent/.env')

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

print("🔍 Checking for email_notification template...\n")

try:
    contents = client.content.v1.contents.list(limit=50)
    
    email_template = None
    for content in contents:
        if 'email' in content.friendly_name.lower() or 'notification' in content.friendly_name.lower():
            print(f"✅ Found: {content.friendly_name}")
            print(f"   SID: {content.sid}")
            print(f"   Language: {content.language}")
            print()
            
            if 'email_notification' in content.friendly_name.lower():
                email_template = content
                break
    
    if email_template:
        print("=" * 60)
        print("🎉 EMAIL NOTIFICATION TEMPLATE FOUND!")
        print("=" * 60)
        print(f"\nAdd this to your .env file:")
        print(f"WHATSAPP_TEMPLATE_SID={email_template.sid}")
        print()
        print("Then restart the services:")
        print("sudo systemctl restart aura-web aura-poller")
        print()
    else:
        print("⏳ Template not found yet. It may still be pending approval.")
        print("   Check again in a few minutes.")
        print()
        print("All templates found:")
        for content in contents:
            print(f"  - {content.friendly_name} ({content.sid})")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
