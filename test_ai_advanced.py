#!/usr/bin/env python3
"""
Advanced AI testing suite for Amy - Edge cases and complex scenarios
"""
import os
import sys
sys.path.insert(0, '/home/peter/aura_agent')

from dotenv import load_dotenv
from services.ai_service import AIService

load_dotenv('/home/peter/aura_agent/.env')

ai_service = AIService()

# Advanced test scenarios
advanced_scenarios = [
    {
        "name": "Emotional/Upset Customer",
        "email": {
            "sender": "angry.customer@company.com",
            "subject": "EXTREMELY DISAPPOINTED with your service",
            "body": """Peter,

I am absolutely furious. We've been waiting 3 WEEKS for a response to our support ticket. This is completely unacceptable for a paying customer.

Your team promised a fix by last Monday. It's now Friday and we've heard NOTHING. This is affecting our entire operation.

I expect an immediate explanation and resolution, or we're canceling our contract.

David Chen
CTO, TechCorp"""
        },
        "instructions": [
            "Apologize sincerely, explain we're investigating, offer call today",
            "Acknowledge frustration but explain we need more details about the ticket number"
        ]
    },
    {
        "name": "Vague/Unclear Instructions",
        "email": {
            "sender": "colleague@company.com",
            "subject": "Thoughts on the proposal?",
            "body": """Hey Peter,

What do you think about the new pricing structure we discussed? Should we move forward?

Let me know.
Sarah"""
        },
        "instructions": [
            "Handle this appropriately",
            "Be diplomatic"
        ]
    },
    {
        "name": "Multi-Recipient (Reply-All Situation)",
        "email": {
            "sender": "team-lead@company.com",
            "subject": "Re: Q4 Planning Meeting",
            "body": """Hi everyone,

Based on the discussion, I think we should prioritize the mobile app over the web redesign. Peter, do you agree?

CC: Sarah (Product), Mike (Engineering), Lisa (Design)

Thanks,
Tom"""
        },
        "instructions": [
            "Agree with Tom's assessment, reply-all",
            "Disagree politely, suggest we need both, reply-all"
        ]
    },
    {
        "name": "Thank You / Appreciation",
        "email": {
            "sender": "client@company.com",
            "subject": "Thank you for the quick turnaround!",
            "body": """Peter,

Just wanted to say thank you for getting that bug fix deployed so quickly yesterday. You saved us from a major issue with our launch.

Really appreciate your team's responsiveness.

Best,
Jennifer"""
        },
        "instructions": [
            "Respond warmly, say it was a team effort",
            "Keep it brief but genuine"
        ]
    },
    {
        "name": "Forwarding Request",
        "email": {
            "sender": "manager@company.com",
            "subject": "Can you handle this?",
            "body": """Peter,

Can you take care of the request below? Client is asking about API rate limits.

---------- Forwarded message ---------
From: support@client.com
Subject: API Rate Limit Questions

We're hitting rate limits on the /users endpoint. Can you increase our limit or explain the current restrictions?

Thanks"""
        },
        "instructions": [
            "Confirm I'll handle it, ask if there's a deadline",
            "Say I'll respond to the client directly with technical details"
        ]
    },
    {
        "name": "Out of Office / Delegation",
        "email": {
            "sender": "partner@company.com",
            "subject": "Urgent: Contract review needed",
            "body": """Peter,

We need your review on the updated contract terms by Monday. Can you take a look?

This is time-sensitive.

Thanks,
Robert"""
        },
        "instructions": [
            "I'm out of office until Wednesday, delegate to Sarah",
            "I'm traveling but will review over the weekend"
        ]
    },
    {
        "name": "Conflicting Instructions",
        "email": {
            "sender": "vendor@company.com",
            "subject": "Price increase notification",
            "body": """Dear Peter,

Effective next month, our pricing will increase by 25% due to infrastructure costs.

Please confirm receipt of this notice.

Best regards,
Vendor Team"""
        },
        "instructions": [
            "Be polite but firm - this is unacceptable, we need to discuss",
            "Acknowledge but don't commit - say we need to review internally"
        ]
    },
    {
        "name": "Spam/Irrelevant Email",
        "email": {
            "sender": "marketing@random-company.com",
            "subject": "You've been selected for our exclusive webinar!",
            "body": """Congratulations Peter!

You've been hand-picked to attend our exclusive webinar on blockchain synergy and AI-powered growth hacking.

Register now for only $499!

Limited spots available!"""
        },
        "instructions": [
            "Ignore this, just unsubscribe",
            "Politely decline"
        ]
    }
]

def test_advanced_scenario(scenario):
    """Test advanced scenarios with edge cases"""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario['name']}")
    print(f"{'='*80}\n")
    
    email = scenario['email']
    
    # Show the summary
    print("📧 EMAIL SUMMARY:")
    print("-" * 80)
    summary = ai_service.summarize_email(
        email['subject'],
        email['sender'],
        email['body']
    )
    print(summary)
    print()
    
    # Test each instruction
    for i, instruction in enumerate(scenario['instructions'], 1):
        print(f"\n💬 INSTRUCTION #{i}: \"{instruction}\"")
        print("-" * 80)
        
        conversation_history = [
            {"role": "user", "content": instruction}
        ]
        
        response = ai_service.generate_response(email, conversation_history)
        print(response)
        print()

def test_multi_turn_conversation():
    """Test multi-turn refinement conversation"""
    print(f"\n{'='*80}")
    print("MULTI-TURN CONVERSATION TEST")
    print(f"{'='*80}\n")
    
    email = {
        "sender": "investor@vc-firm.com",
        "subject": "Investment opportunity discussion",
        "body": """Hi Peter,

I'd like to discuss a potential investment in your company. Are you open to a conversation?

We're particularly interested in your AI capabilities.

Best,
Alex"""
    }
    
    print("📧 EMAIL:")
    print(f"From: {email['sender']}")
    print(f"Subject: {email['subject']}\n")
    
    # Simulate a multi-turn conversation
    turns = [
        ("Draft a response saying we're interested", None),
        ("Make it more enthusiastic", None),
        ("Actually, tone it down - be professional but not overeager", None),
        ("Add that we're also interested in their portfolio companies", None)
    ]
    
    conversation_history = []
    
    for turn_num, (instruction, _) in enumerate(turns, 1):
        print(f"\n{'─'*80}")
        print(f"TURN {turn_num}: \"{instruction}\"")
        print("─" * 80)
        
        conversation_history.append({"role": "user", "content": instruction})
        response = ai_service.generate_response(email, conversation_history)
        conversation_history.append({"role": "assistant", "content": response})
        
        print(response)

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  AMY ADVANCED AI BEHAVIOR TEST SUITE                         ║
║                                                                              ║
║  Testing edge cases, emotional emails, vague instructions, and               ║
║  multi-turn conversations to ensure robustness.                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Test all advanced scenarios
    for scenario in advanced_scenarios:
        test_advanced_scenario(scenario)
    
    # Test multi-turn conversation
    test_multi_turn_conversation()
    
    print("\n" + "="*80)
    print("ADVANCED TESTING COMPLETE")
    print("="*80)
    print("\nKEY EVALUATION CRITERIA:")
    print("  ✓ Handles emotional emails with appropriate empathy")
    print("  ✓ Makes reasonable decisions with vague instructions")
    print("  ✓ Adapts tone based on context (upset customer vs thank you)")
    print("  ✓ Maintains consistency across multi-turn refinements")
    print("  ✓ Recognizes spam/irrelevant emails")
    print("  ✓ Handles delegation and out-of-office scenarios")

if __name__ == "__main__":
    main()
