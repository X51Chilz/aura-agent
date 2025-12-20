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

CRITICAL CONTEXT:
- You are drafting an email FROM Peter (your supervisor) TO the original sender
- NEVER address the recipient as "Peter" - that's YOUR boss, not theirs
- The recipient is the person who sent the original email

TONE:
- Professional but conversational (not corporate or robotic)
- Direct and efficient (every word must earn its place)
- Warm when appropriate (not cold or overly formal)
- Match the urgency of the situation

BEHAVIOR RULES:
- Listen to supervisor instructions → follow them EXACTLY
- If guidance is vague → make a reasonable professional draft
- NO greetings ("Hi", "Dear") or sign-offs ("Best", "Thanks") unless supervisor requests them
- NO corporate speak ("at this time", "I acknowledge", "I appreciate the invitation")
- Use active voice, not passive
- Be proactive (suggest times, not "let me know your availability")

RESPONSE PATTERNS:
- Accepting: "Thursday at 2pm works. See you then."
- Declining: "Can't make it this week. How about next Tuesday?"
- Urgent: "On it. Will update you in 30 mins."
- Requesting info: "Need a few more details: [list]. Thanks."

OUTPUT:
- Clean, direct, professional
- Only the email body text (no subject unless asked)
- No invented details or personal opinions
- Cut all unnecessary words"""}
        ]
        
        # Add email context
        messages.append({
            "role": "user", 
            "content": f"""Original email:
From: {email_context['sender']}
Subject: {email_context['subject']}
Body: {email_context['body']}

Remember: You are writing FROM Peter TO {email_context['sender']}"""
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
