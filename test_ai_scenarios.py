#!/usr/bin/env python3
"""
Test script for evaluating Amy's AI behavior with realistic email scenarios.
Run this to test different email types and supervisor instructions.
"""
import os
import sys
sys.path.insert(0, '/home/peter/aura_agent')

from dotenv import load_dotenv
from services.ai_service import AIService

load_dotenv('/home/peter/aura_agent/.env')

ai_service = AIService()

# Test scenarios with different email types
scenarios = [
    {
        "name": "Meeting Request",
        "email": {
            "sender": "john.smith@company.com",
            "subject": "Quick sync on Q1 planning",
            "body": """Hi Peter,

Hope you're doing well! I wanted to see if you have 30 minutes this week to discuss our Q1 planning. We need to align on priorities and resource allocation.

Would Thursday 2pm or Friday 10am work for you?

Best,
John"""
        },
        "instructions": [
            "Accept Thursday 2pm",
            "Decline politely, suggest next week instead",
            "Ask for agenda before committing"
        ]
    },
    {
        "name": "Sales Pitch",
        "email": {
            "sender": "sales@saasplatform.com",
            "subject": "Increase your team's productivity by 40%",
            "body": """Hi Peter,

I noticed your company is growing fast. Our platform helps teams like yours save 10+ hours per week through automated workflows.

Can I schedule a 15-minute demo to show you how we can help?

Looking forward to connecting!
Sarah"""
        },
        "instructions": [
            "Politely decline, not interested",
            "Say we're evaluating options, ask for pricing sheet",
        ]
    },
    {
        "name": "Urgent Bug Report",
        "email": {
            "sender": "support@client.com",
            "subject": "URGENT: Production issue affecting 500 users",
            "body": """Peter,

We're experiencing a critical issue in production. The payment processing is failing for all users since 9am. This is affecting approximately 500 customers.

Error message: "Payment gateway timeout"

Can you investigate ASAP? Our team is standing by.

Thanks,
Mike"""
        },
        "instructions": [
            "Acknowledge urgency, say investigating now, will update in 30 mins",
            "Ask for more details: error logs, exact time it started, which payment gateway"
        ]
    }
]

def test_scenario(scenario):
    """Test a single scenario with multiple instruction variations"""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario['name']}")
    print(f"{'='*80}\n")
    
    email = scenario['email']
    
    # First, show the summary
    print("📧 EMAIL SUMMARY (What supervisor sees on WhatsApp):")
    print("-" * 80)
    summary = ai_service.summarize_email(
        email['subject'],
        email['sender'],
        email['body']
    )
    print(summary)
    print()
    
    # Test each instruction variation
    for i, instruction in enumerate(scenario['instructions'], 1):
        print(f"\n💬 INSTRUCTION #{i}: \"{instruction}\"")
        print("-" * 80)
        
        conversation_history = [
            {"role": "user", "content": instruction}
        ]
        
        response = ai_service.generate_response(email, conversation_history)
        print(response)
        print()

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     AMY AI BEHAVIOR TEST SUITE                               ║
║                                                                              ║
║  This script tests Amy's responses to realistic email scenarios.            ║
║  Review the outputs to see if Amy follows instructions correctly.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    for scenario in scenarios:
        test_scenario(scenario)
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nREVIEW CHECKLIST:")
    print("  ✓ Does Amy follow supervisor instructions exactly?")
    print("  ✓ Is the tone professional and appropriate?")
    print("  ✓ Does Amy avoid adding unnecessary details?")
    print("  ✓ Are summaries concise and actionable?")
    print("\nIf any issues found, update prompts in services/ai_service.py")

if __name__ == "__main__":
    main()
