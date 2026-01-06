from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv
import uvicorn
import os
import time
from services.gmail_service import GmailService
from services.ai_service import AIService
from services.whatsapp_service import WhatsAppService
from utils.db import Database

import sys

# Force unbuffered output for systemd logging
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

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
@app.post("/webhook/49b779dd-95a5-423b-8cbc-4daf91af44c8/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages from supervisor"""
    # Log RAW request details for debugging
    headers = dict(request.headers)
    body = await request.body()
    form_data = await request.form()
    
    incoming_msg = form_data.get("Body", "").strip()
    from_number = form_data.get("From", "")
    
    print(f"DEBUG: Webhook hit! Path: {request.url.path}")
    print(f"DEBUG: Headers: {headers}")
    print(f"DEBUG: Raw Body: {body.decode(errors='ignore')}")
    print(f"DEBUG: Form Data: {dict(form_data)}")
    
    if not from_number:
        print("⚠️ Received webhook with NO 'From' number. Likely a scanner or misconfigured proxy.")
        return {"status": "error", "message": "Missing From number"}

    print(f"Received WhatsApp message: {incoming_msg} from {from_number}")
    
    # Get the most recent pending thread
    pending_threads = db.get_pending_threads()
    
    if not pending_threads:
        whatsapp_service.send_message(from_number, "No pending emails right now. You're all caught up! 👍")
        return {"status": "ok"}
    
    # Work with the most recent thread
    thread = pending_threads[0]
    email_id = thread['email_id']
    
    # Get email context
    email_context = {
        "sender": thread['sender'],
        "subject": thread['subject'],
        "body": thread['body']
    }
    
    # Get conversation history
    conversation_history = db.get_conversation_history(email_id)
    
    # Get AI response (Single Brain)
    try:
        response = ai_service.get_response(incoming_msg, email_context, conversation_history)
        print(f"DEBUG: AI Response: {response}")
    except Exception as e:
        print(f"❌ Error getting AI response: {e}")
        whatsapp_service.send_message(from_number, "Sorry, I'm having trouble thinking right now. 🧠❌")
        return {"status": "error"}

    # Update conversation history with user message and AI response
    conversation_history.append({"role": "user", "content": incoming_msg})
    conversation_history.append({"role": "assistant", "content": response})
    db.update_conversation(email_id, conversation_history)

    # Check for SEND SIGNAL
    if "[SIGNAL: SEND_EMAIL]" in response:
        print("🚀 Send signal detected!")
        # Clean the response for WhatsApp (remove the signal marker)
        whatsapp_msg = response.replace("[SIGNAL: SEND_EMAIL]", "").strip()
        
        # Find the most recent draft in history
        # We look through history (including the current response) for a --- block
        draft_body = None
        import re
        
        # Search backwards through messages starting from the current one
        for msg in reversed(conversation_history):
            content = msg['content']
            # Find content between --- markers
            # Matches --- followed by anything (non-greedy) followed by ---
            match = re.search(r'---\s*(.*?)\s*---', content, re.DOTALL)
            if match:
                draft_body = match.group(1).strip()
                break
        
        if draft_body:
            try:
                gmail_service.send_email(
                    to=thread['sender'],
                    subject=f"Re: {thread['subject']}",
                    body=draft_body,
                    in_reply_to=thread.get('message_id'),
                    references=thread.get('email_references'),
                    thread_id=thread.get('thread_id')
                )
                gmail_service.mark_as_read(email_id)
                db.update_status(email_id, "SENT")
                db.update_draft_response(email_id, draft_body) # Keep track of what we sent
                
                # Send the AI's chat response (the "Done! Sent." part)
                whatsapp_service.send_message(from_number, whatsapp_msg)
                print(f"✅ Email sent successfully using draft: {draft_body[:50]}...")
            except Exception as send_error:
                print(f"❌ Error sending email: {send_error}")
                whatsapp_service.send_message(from_number, f"❌ I tried to send it, but hit an error: {str(send_error)}")
        else:
            whatsapp_service.send_message(from_number, "I was ready to send, but I couldn't find the draft in our conversation. Can you show it to me again?")
            print("⚠️ Send signal detected but no '---' block found in history.")
    else:
        # Just a normal conversation turn
        whatsapp_service.send_message(from_number, response)
        print(f"✅ Conversational reply sent to {from_number}")

    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "Aura Agent is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
