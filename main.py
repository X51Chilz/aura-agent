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
                    body=draft,
                    in_reply_to=thread.get('message_id'),
                    references=thread.get('email_references'),
                    thread_id=thread.get('thread_id')
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

@app.get("/")
async def root():
    return {"status": "Aura Agent is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"status": "Aura Agent is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
