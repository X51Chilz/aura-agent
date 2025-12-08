import os
from openai import OpenAI

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def summarize_email(self, subject, sender, body):
        """Summarize an email for the supervisor"""
        prompt = f"""Email from: {sender}
Subject: {subject}

Body:
{body}

Provide a sharp, concise summary (2-3 sentences max):
- Sender's intent
- Key facts
- Action items or expectations

No opinions. No invented details. Just the facts."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Amy, a concise and highly competent AI email assistant. Be smart, sharp, and efficient. No fluff, no drama. Capture only what matters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )
        
        return response.choices[0].message.content
    
    def generate_response(self, email_context, conversation_history):
        """Generate or refine an email response based on conversation with supervisor"""
        messages = [
            {"role": "system", "content": """You are Amy, a sharp and efficient AI email assistant.

BEHAVIOR RULES:
- Listen carefully to supervisor instructions → follow them EXACTLY
- If guidance is vague → make a reasonable professional draft
- Maintain polite, clear, professional email tone
- NO greetings or sign-offs unless supervisor requests them
- NO fluff, NO drama
- Adapt instantly to feedback

OUTPUT:
- Clean, direct, professional
- Only the email body text (no subject unless asked)
- No invented details or personal opinions"""}
        ]
        
        # Add email context
        messages.append({
            "role": "user", 
            "content": f"Original email:\nFrom: {email_context['sender']}\nSubject: {email_context['subject']}\nBody: {email_context['body']}"
        })
        
        # Add conversation history
        messages.extend(conversation_history)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.6,
            max_tokens=400
        )
        
        return response.choices[0].message.content
