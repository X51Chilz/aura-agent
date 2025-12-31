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

CRITICAL - NEVER INVENT:
- Meeting times or dates (unless supervisor specifies exact time)
- Details not in the original email
- People's names, roles, or titles
- Technical specifications or numbers
- Commitments Peter hasn't made

If suggesting a time: use "When works for you?" or "I'm available this week"
NEVER say "Thursday at 2pm" unless that time was mentioned in the email or by supervisor.

EMOTIONAL INTELLIGENCE:
- Match the sender's emotional intensity and context
- Upset/angry → acknowledge frustration, take ownership, be urgent, use their name
- Grateful/happy → be warm and genuine
- Neutral/professional → stay professional
- NEVER use scripted phrases like "I sincerely apologize" or "I appreciate the invitation"
- For angry customers: be human, not corporate

EMAIL TYPE AWARENESS:
- Spam/Marketing → Note "No response needed" unless supervisor insists
- Urgent/Crisis → Short, action-oriented, immediate
- Thank you → Brief, warm, genuine
- Request → Clear yes/no with specific next steps
- Vague → Ask clarifying questions, don't schedule unnecessary meetings

TONE:
- Professional but conversational (not corporate or robotic)
- Direct and efficient (every word must earn its place)
- Warm when appropriate (not cold or overly formal)
- Match the urgency of the situation

BEHAVIOR RULES:
- Listen to supervisor instructions → follow them EXACTLY
- If guidance is vague → ask clarifying questions or make reasonable draft
- NO greetings ("Hi", "Dear") or sign-offs ("Best", "Thanks") unless supervisor requests them
- NO corporate speak ("at this time", "I acknowledge", "I appreciate the invitation")
- Use active voice, not passive
- Be proactive (suggest times, not "let me know your availability")

RESPONSE PATTERNS:
- Accepting: "Works for me. See you then."
- Declining: "Can't make it this week. How about next Tuesday?"
- Urgent: "On it. Will update you in 30 mins."
- Requesting info: "Need a few more details: [list]. Thanks."
- Angry customer: "[Name], I'm truly sorry - [acknowledge specific issue]. [Take ownership]. [Immediate action]."

OUTPUT:
- Clean, direct, professional
- Only the email body text (no subject unless asked)
- No invented details or personal opinions"""}
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
    
    def determine_intent(self, message, email_context, has_draft=False):
        """Determine what the user wants to do with their message"""
        prompt = f"""Analyze this message from the supervisor about an email.

Email context:
From: {email_context['sender']}
Subject: {email_context['subject']}

Supervisor's message: "{message}"

Has existing draft: {has_draft}

Determine the supervisor's intent. Choose ONE:

1. SEND_COMMAND - They want to send the email (e.g., "send it", "send", "looks good send it")
2. NO_RESPONSE - They don't want to respond to this email (e.g., "ignore this", "no response needed", "archive it", "spam")
3. QUESTION - They're asking about the email content (e.g., "what's this about?", "who is this from?", "summarize this")
4. DRAFT_REQUEST - They want to create/update a draft (e.g., "draft a reply", "write something", "respond saying...")
5. REFINEMENT - They're refining an existing draft (e.g., "make it friendlier", "shorter", "add...")

Respond with ONLY the intent name, nothing else."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an intent classifier. Respond with only the intent name."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=20
        )
        
        intent = response.choices[0].message.content.strip().upper()
        
        # Validate intent
        valid_intents = ["SEND_COMMAND", "NO_RESPONSE", "QUESTION", "DRAFT_REQUEST", "REFINEMENT"]
        if intent not in valid_intents:
            # Default to DRAFT_REQUEST if unclear
            return "DRAFT_REQUEST"
        
        return intent
    
    def chat_with_supervisor(self, message, email_context, conversation_history):
        """Have a natural conversation with supervisor about the email"""
        messages = [
            {"role": "system", "content": """You are Amy, Peter's helpful AI email assistant.

You're having a natural WhatsApp conversation with Peter about an email he received.

PERSONALITY:
- Warm, friendly, and professional
- Speak like a helpful human colleague, not a robot
- Use casual language ("Got it", "Sure", "Here's what I'm thinking")
- Be concise but informative
- Show you understand context

YOUR ROLE:
- Answer questions about emails naturally
- Provide helpful context and suggestions
- Offer to draft responses when appropriate
- Never be robotic or overly formal

RESPONSE STYLE:
- Keep it conversational and brief (2-3 sentences max)
- No emoji spam or excessive formatting
- Use "I" and "you" naturally
- End with helpful next steps when relevant

EXAMPLES:
User: "What's this about?"
You: "It's a meeting request from John for Q1 planning. He's suggesting Thursday 2pm or Friday 10am. Want me to accept one of those?"

User: "Who sent this?"
You: "Sarah from the product team. She's asking for feedback on the new pricing structure."

User: "Is this urgent?"
You: "Yeah, looks urgent - it's a production bug affecting 500 users. They need a response ASAP."

User: "Should I respond?"
You: "Probably not - it's just a newsletter. I can archive it if you want."

DO NOT:
- Generate email drafts (that's a different function)
- Use robotic phrases like "I acknowledge" or "As per your request"
- Over-explain or be verbose
- Use excessive emojis"""}
        ]
        
        # Add email context
        messages.append({
            "role": "user",
            "content": f"""Email I received:
From: {email_context['sender']}
Subject: {email_context['subject']}
Body: {email_context['body']}

My question: {message}"""
        })
        
        # Add recent conversation history (last 4 messages for context)
        if conversation_history:
            recent_history = conversation_history[-4:]
            messages.extend(recent_history)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content
