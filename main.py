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
    
    # Check if we have a draft
    has_draft = thread.get('draft_response') is not None
    
    # Determine user's intent
    try:
        intent = ai_service.determine_intent(incoming_msg, email_context, has_draft)
        print(f"Detected intent: {intent}")
    except Exception as e:
        print(f"Error detecting intent: {e}")
        intent = "DRAFT_REQUEST"  # Safe fallback
    
    # Route based on intent
    if intent == "SEND_COMMAND":
        # User wants to send the email
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
                whatsapp_service.send_message(from_number, "✅ Sent!")
                print(f"✅ Email sent to {thread['sender']}")
            except Exception as send_error:
                print(f"❌ Error sending email: {send_error}")
                whatsapp_service.send_message(from_number, f"❌ Couldn't send: {str(send_error)}")
        else:
            whatsapp_service.send_message(from_number, "No draft to send yet. Want me to write something first?")
    
    elif intent == "NO_RESPONSE":
        # User doesn't want to respond to this email
        try:
            gmail_service.mark_as_read(email_id)
            db.update_status(email_id, "NO_RESPONSE")
            whatsapp_service.send_message(from_number, "Got it. Marked as handled, no response sent.")
            print(f"✅ Email marked as no response needed: {email_id}")
        except Exception as e:
            print(f"❌ Error marking as no response: {e}")
            whatsapp_service.send_message(from_number, "Okay, I'll skip this one.")
    
    elif intent == "QUESTION":
        # User is asking about the email
        try:
            response = ai_service.chat_with_supervisor(incoming_msg, email_context, conversation_history)
            
            # Store conversation
            conversation_history.append({"role": "user", "content": incoming_msg})
            conversation_history.append({"role": "assistant", "content": response})
            db.update_conversation(email_id, conversation_history)
            
            whatsapp_service.send_message(from_number, response)
            print(f"✅ Answered question about email: {email_id}")
        except Exception as e:
            print(f"❌ Error in chat: {e}")
            whatsapp_service.send_message(from_number, "Sorry, had trouble with that. Can you rephrase?")
    
    elif intent == "DRAFT_REQUEST" or intent == "REFINEMENT":
        # User wants to create or refine a draft
        try:
            conversation_history.append({"role": "user", "content": incoming_msg})
            
            # Generate/refine draft
            draft_response = ai_service.generate_response(email_context, conversation_history)
            
            # Store conversation and draft
            conversation_history.append({"role": "assistant", "content": draft_response})
            db.update_conversation(email_id, conversation_history)
            db.update_draft_response(email_id, draft_response)
            
            # Send draft with natural language
            if intent == "REFINEMENT":
                response_text = f"How's this:\n\n{draft_response}\n\nBetter?"
            else:
                response_text = f"Here's what I'm thinking:\n\n{draft_response}\n\nWant me to adjust anything?"
            
            whatsapp_service.send_message(from_number, response_text)
            print(f"✅ Generated draft for email: {email_id}")
        except Exception as e:
            print(f"❌ Error generating draft: {e}")
            import traceback
            traceback.print_exc()
            whatsapp_service.send_message(from_number, f"Had trouble with that: {str(e)}")
    
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"status": "Aura Agent is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
