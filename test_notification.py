#!/usr/bin/env python3
"""Test script to send WhatsApp notification for pending email"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/peter/aura_agent/.env')

# Add parent directory to path
sys.path.insert(0, '/home/peter/aura_agent')

from utils.db import Database
from services.whatsapp_service import WhatsAppService

# Get pending email
db = Database('/home/peter/aura_agent/aura_agent.db')
threads = db.get_pending_threads()

if threads:
    thread = threads[0]
    print(f"✅ Found pending email: {thread['subject']}")
    print(f"   From: {thread['sender']}")
    
    # Send WhatsApp notification
    whatsapp = WhatsAppService()
    supervisor = os.getenv("SUPERVISOR_WHATSAPP")
    
    notification = f"""📨 New Email Received!

From: {thread['sender']}
Subject: {thread['subject']}

Summary:
{thread['summary']}

---
Reply with instructions on how to respond."""
    
    try:
        whatsapp.send_message(supervisor, notification)
        print(f"✅ WhatsApp notification sent to {supervisor}")
    except Exception as e:
        print(f"❌ WhatsApp error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("ℹ️  No pending emails to test with")
