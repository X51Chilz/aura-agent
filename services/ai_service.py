import os
from openai import OpenAI

class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def summarize_email(self, subject, sender, body):
        """Summarize an email for the supervisor"""
        prompt = f"""You are an AI assistant helping to summarize emails. 
        
Email Details:
From: {sender}
Subject: {subject}

Body:
{body}

Please provide a concise summary of this email in 2-3 sentences, focusing on the key points and any action items."""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful email assistant that summarizes emails concisely."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content
    
    def generate_response(self, email_context, conversation_history):
        """Generate or refine an email response based on conversation with supervisor"""
        messages = [
            {"role": "system", "content": """You are an AI email assistant. Your supervisor is helping you craft a response to an email. 
            
Based on the conversation, generate a professional email response. If the supervisor gives you specific instructions, follow them carefully.
Only output the email body text, no subject line or greetings unless specifically requested."""}
        ]
        
        # Add email context
        messages.append({
            "role": "user", 
            "content": f"Original email context:\nFrom: {email_context['sender']}\nSubject: {email_context['subject']}\nBody: {email_context['body']}"
        })
        
        # Add conversation history
        messages.extend(conversation_history)
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
