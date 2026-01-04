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
                # FIRST ATTEMPT: Send using Template
                if template_sid:
                    try:
                        # Sanitize variables to prevent WhatsApp Template Error 63005
                        # 1. Clean Sender: Revert to standard safe formatting
                        # "Peter Mares <email>" -> "Peter Mares <email>" (if valid chars)
                        clean_sender = email_content['sender'].strip()[:50]
                            
                        # 2. Clean Subject: Remove newlines, allow only safe chars
                        clean_subject = email_content['subject'].replace('\n', ' ').strip()[:50]
                        
                        # 3. Clean Summary: MUST remove newlines (Error 21656) but allowed longer length
                        clean_summary = summary.replace('\n', ' ').strip()[:1000]
                        
                        whatsapp_service.send_template_message(
                            SUPERVISOR_WHATSAPP,
                            template_sid,
                            [
                                clean_sender,      # {{1}}
                                clean_subject,     # {{2}}
                                clean_summary      # {{3}}
                            ]
                        )
                        print(f"✅ Sent template notification to supervisor: {email_id}")
                        
                    except Exception as template_error:
                        print(f"⚠️ Template failed ({template_error}), falling back to text message...")
                        # FALLBACK: Send as standard text message
                        notification = f"""📨 New Email from {clean_sender}
Subject: {clean_subject}

{summary}

---
Reply with instructions."""
                        whatsapp_service.send_message(SUPERVISOR_WHATSAPP, notification)
                        print(f"✅ Sent fallback WhatsApp notification: {email_id}")
                
                else:
                    # No template configured, use standard text
                    notification = f"""📨 New Email
From: {email_content['sender']}
Subject: {email_content['subject']}

{summary}

---
Reply with instructions."""
                    
                    whatsapp_service.send_message(SUPERVISOR_WHATSAPP, notification)
                    print(f"✅ Sent WhatsApp notification: {email_id}")
                
                # Mark as read in Gmail
                gmail_service.mark_as_read(email_id)
                print(f"✅ Marked email as read: {email_id}")
                
            except Exception as whatsapp_error:
                print(f"❌ Failed to send WhatsApp notification: {whatsapp_error}")
                import traceback
                traceback.print_exc()
        
        # Check every 60 seconds
        time.sleep(60)
        
    except Exception as e:
        print(f"❌ Error checking emails: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(60)
