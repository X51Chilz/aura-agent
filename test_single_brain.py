import os
import sys
from unittest.mock import MagicMock
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.getcwd())

from services.ai_service import AIService

def test_flow():
    load_dotenv()
    ai = AIService()
    
    email_context = {
        "sender": "John Doe <john@example.com>",
        "subject": "Project Update",
        "body": "Hi Peter, just checking in on the project status. Can we meet tomorrow?"
    }
    
    history = []
    
    # Turn 1: Question
    print("\n--- TURN 1: QUESTION ---")
    msg1 = "What does he want?"
    res1 = ai.get_response(msg1, email_context, history)
    print(f"Peter: {msg1}")
    print(f"Amy: {res1}")
    history.append({"role": "user", "content": msg1})
    history.append({"role": "assistant", "content": res1})
    
    # Turn 2: Draft request
    print("\n--- TURN 2: DRAFT REQUEST ---")
    msg2 = "Draft a polite reply saying I'm busy tomorrow but free on Friday 10am."
    res2 = ai.get_response(msg2, email_context, history)
    print(f"Peter: {msg2}")
    print(f"Amy: {res2}")
    history.append({"role": "user", "content": msg2})
    history.append({"role": "assistant", "content": res2})
    
    # Turn 3: Refinement
    print("\n--- TURN 3: REFINEMENT ---")
    msg3 = "Actually make it Thursday at 3pm."
    res3 = ai.get_response(msg3, email_context, history)
    print(f"Peter: {msg3}")
    print(f"Amy: {res3}")
    history.append({"role": "user", "content": msg3})
    history.append({"role": "assistant", "content": res3})
    
    # Turn 4: Send
    print("\n--- TURN 4: SEND ---")
    msg4 = "Perfect, send it."
    res4 = ai.get_response(msg4, email_context, history)
    print(f"Peter: {msg4}")
    print(f"Amy: {res4}")
    
    if "[SIGNAL: SEND_EMAIL]" in res4:
        print("\n✅ Signal Detected!")
        
        # Test the draft extraction logic from main.py
        import re
        draft_body = None
        # Include current response in history for simulation
        full_history = history + [{"role": "assistant", "content": res4}]
        for msg in reversed(full_history):
            content = msg['content']
            match = re.search(r'---\s*(.*?)\s*---', content, re.DOTALL)
            if match:
                draft_body = match.group(1).strip()
                break
        
        if draft_body:
            print(f"✅ Extracted Draft:\n{draft_body}")
        else:
            print("❌ Draft extraction failed!")
    else:
        print("❌ Signal NOT detected!")

if __name__ == "__main__":
    test_flow()
