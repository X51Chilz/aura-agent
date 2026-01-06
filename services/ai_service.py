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
    
    def get_response(self, message, email_context, conversation_history):
        """Unified conversational brain for chatting and drafting"""
        system_prompt = f"""You are Amy, Peter's highly competent and warm AI Assistant. 
You help Peter manage his emails via WhatsApp.

PERSONALITY & TONE:
- Professional, efficient, and genuinely helpful.
- Speak like a colleague/partner, not a robotic script.
- Use natural language ("Got it", "On it", "I've drafted that for you").
- You have a personality: you are smart, proactive, and protective of Peter's time.

YOUR GOAL:
- Discuss emails with Peter, answer his questions, and help him draft replies.
- You are writing drafts FROM Peter TO the original sender.
- When drafting, include a professional sign-off like "Best, Amy" or "Thanks, Amy" at the very end of the email body, as Peter's signature block is automatically appended after yours.

CONVERSATION RULES:
1. Be concise but human. WhatsApp is for quick communication.
2. Maintain full context of the entire conversation.
3. If Peter asks a question ("Who is this from?"), answer it directly.
4. If Peter asks to draft/respond, provide a high-quality draft.
5. **DRAFT FORMATTING:** Always wrap the actual email body you are proposing in triple dashes (`---`) so it stands out from your chat. For example:
   "Sure, here's a draft:
   ---
   Hi John,
   ...
   Best, Amy
   ---
   What do you think?"
6. You can brainstorm and draft in the same message if it makes sense.
7. NEVER invent facts (meeting times, technical specs) not found in the email or Peter's instructions.

TRIGGERING ACTIONS:
- If Peter confirms he is happy with a draft and wants to send it (e.g., "send it", "looks good", "GO"), you MUST append the exact marker `[SIGNAL: SEND_EMAIL]` to the very end of your message.
- If the send signal is present, the system will automatically send the content of the **most recent** `---` block found in the conversation history. Ensure the most recent block contains the final, correct version Peter approved.

RECIPIENT CONTEXT:
Original Email From: {email_context['sender']}
Subject: {email_context['subject']}
Body: {email_context['body']}

Remember: You are Peter's EA. You are talking to Peter, but drafting for {email_context['sender']}."""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add the new message
        messages.append({"role": "user", "content": message})
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
