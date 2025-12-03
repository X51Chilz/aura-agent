from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv
import uvicorn
import os
import time
from services.gmail_service import GmailService
from services.ai_service import AIService
from services.whatsapp_service import WhatsAppService
from utils.db import Database

load_dotenv()

app = FastAPI()

# Initialize services
gmail_service = GmailService()
ai_service = AIService()
whatsapp_service = WhatsAppService()
db = Database()

# Supervisor's WhatsApp number (you'll need to add this to .env)
SUPERVISOR_WHATSAPP = os.getenv("SUPERVISOR_WHATSAPP")

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages from supervisor"""
    form_data = await request.form()
    
    incoming_msg = form_data.get("Body", "").strip()
    from_number = form_data.get("From", "")
    
    print(f"Received WhatsApp message: {incoming_msg} from {from_number}")
    
    # Get the most recent pending thread
    pending_threads = db.get_pending_threads()
    
    if not pending_threads:
        whatsapp_service.send_message(from_number, "No pending emails to respond to.")
        return {"status": "ok"}
    
    # Work with the most recent thread
    thread = pending_threads[0]
    email_id = thread['email_id']
    
    # Parse supervisor commands
    incoming_lower = incoming_msg.lower()
    
    if "send it" in incoming_lower or "send" == incoming_lower:
        # Send the draft response
        draft = thread.get('draft_response')
        if draft:
            try:
                gmail_service.send_email(
                    to=thread['sender'],
                    subject=f"Re: {thread['subject']}",
                    body=draft
                )
                gmail_service.mark_as_read(email_id)
                db.update_status(email_id, "SENT")
                whatsapp_service.send_message(from_number, "✅ Email sent successfully!")
                print(f"✅ Email sent to {thread['sender']}")
            except Exception as send_error:
                print(f"❌ Error sending email: {send_error}")
                import traceback
                traceback.print_exc()
                whatsapp_service.send_message(from_number, f"❌ Error sending email: {str(send_error)}")
        else:
            whatsapp_service.send_message(from_number, "No draft response available. Please provide instructions first.")
    
    else:
        # Supervisor is providing feedback/instructions
        conversation_history = db.get_conversation_history(email_id)
        conversation_history.append({"role": "user", "content": incoming_msg})
        
        # Generate response based on conversation
        email_context = {
            "sender": thread['sender'],
            "subject": thread['subject'],
            "body": thread['body']
        }
        
        draft_response = ai_service.generate_response(email_context, conversation_history)
        
        # Store the conversation and draft
        conversation_history.append({"role": "assistant", "content": draft_response})
        db.update_conversation(email_id, conversation_history)
        db.update_draft_response(email_id, draft_response)
        
        # Send draft back to supervisor
        whatsapp_service.send_message(
            from_number,
            f"📧 Draft response:\n\n{draft_response}\n\n---\nReply with feedback or say 'send it' to approve."
        )
    
    return {"status": "ok"}

def check_new_emails():
    """Background task to check for new emails"""
    while True:
        try:
            print("Checking for new emails...")
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
                    summary=summary
                )
                
                # Notify supervisor via WhatsApp
                notification = f"""📨 New Email Received!

From: {email_content['sender']}
Subject: {email_content['subject']}

Summary:
{summary}

---
Reply with instructions on how to respond."""
                
                try:
                    whatsapp_service.send_message(SUPERVISOR_WHATSAPP, notification)
                    print(f"✅ Notified supervisor about email: {email_id}")
                except Exception as whatsapp_error:
                    print(f"❌ Failed to send WhatsApp notification: {whatsapp_error}")
                    print(f"Supervisor number: {SUPERVISOR_WHATSAPP}")
                    import traceback
                    traceback.print_exc()
            
            # Check every 60 seconds
            time.sleep(60)
            
        except Exception as e:
            print(f"Error checking emails: {e}")
            time.sleep(60)

@app.on_event("startup")
async def startup_event():
    """Start background email checking on startup"""
    import threading
    email_thread = threading.Thread(target=check_new_emails, daemon=True)
    email_thread.start()
    print("Email checking thread started")

@app.get("/")
async def root():
    return {"status": "Aura Agent is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
