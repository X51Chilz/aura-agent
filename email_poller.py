#!/usr/bin/env python3 -u
"""
Standalone email poller that runs independently from the web server.
Checks Gmail every 60 seconds and sends WhatsApp notifications.
"""
import os
import sys
import time
from dotenv import load_dotenv

# Force unbuffered output for systemd logging
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Load environment variables
load_dotenv()

# Import services
from services.gmail_service import GmailService
from services.ai_service import AIService
from services.whatsapp_service import WhatsAppService
from utils.db import Database

# Initialize services
print("🚀 Initializing Aura Agent Email Poller...")
gmail_service = GmailService()
ai_service = AIService()
whatsapp_service = WhatsAppService()
db = Database()

SUPERVISOR_WHATSAPP = os.getenv("SUPERVISOR_WHATSAPP")

print(f"✅ Services initialized. Supervisor: {SUPERVISOR_WHATSAPP}")
print("📧 Starting email polling loop...")

while True:
    try:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Checking for new emails...")
        unread_emails = gmail_service.list_unread_emails()
        
        for email_msg in unread_emails:
            email_id = email_msg['id']
            
            # Check if we've already processed this email
            existing_thread = db.get_thread_by_email_id(email_id)
            if existing_thread:
                continue
            
            # Get email content
            email_content = gmail_service.get_email_content(email_id)
            
            # Summarize with AI
            summary = ai_service.summarize_email(
                email_content['subject'],
                email_content['sender'],
                email_content['body']
            )
            
            # Store in database
            db.create_thread(
                email_id=email_id,
                sender=email_content['sender'],
                subject=email_content['subject'],
                body=email_content['body'],
                summary=summary,
                message_id=email_content.get('message_id'),
                references=email_content.get('references'),
                thread_id=email_msg.get('threadId')
            )
            
            
            # Notify supervisor via WhatsApp using template
            template_sid = os.getenv("WHATSAPP_TEMPLATE_SID")
            
            try:
                if template_sid:
                    # Use approved template (production-ready)
                    whatsapp_service.send_template_message(
                        SUPERVISOR_WHATSAPP,
                        template_sid,
                        [
                            email_content['sender'],      # {{1}}
                            email_content['subject'],     # {{2}}
                            summary                        # {{3}}
                        ]
                    )
                    print(f"✅ Sent template notification to supervisor: {email_id}")
                else:
                    # Fallback to freeform message (requires 24hr window)
                    notification = f"""📨 New Email

From: {email_content['sender']}
Subject: {email_content['subject']}

{summary}

---
Reply with instructions."""
                    
                    whatsapp_service.send_message(SUPERVISOR_WHATSAPP, notification)
                print(f"✅ Sent WhatsApp notification: {email_id}")
                
                # Mark as read in Gmail so it doesn't clutter inbox
                # (Poller relies on DB check to avoid duplicates)
                gmail_service.mark_as_read(email_id)
                print(f"✅ Marked email as read: {email_id}")
                
            except Exception as whatsapp_error:
                print(f"❌ Failed to send WhatsApp notification: {whatsapp_error}")
                print(f"Supervisor number: {SUPERVISOR_WHATSAPP}")
                import traceback
                traceback.print_exc()
        
        # Check every 60 seconds
        time.sleep(60)
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(60)
