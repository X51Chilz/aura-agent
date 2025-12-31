#!/usr/bin/env python3
"""
Test script for conversational AI improvements
Tests intent detection and natural conversation flow
"""
import os
import sys
sys.path.insert(0, '/home/peter/aura_agent')

from dotenv import load_dotenv
load_dotenv('/home/peter/aura_agent/.env')

from services.ai_service import AIService

ai = AIService()

# Test email context
email_context = {
    "sender": "john.smith@company.com",
    "subject": "Q1 Planning Meeting",
    "body": "Hi Peter, Can we schedule a 30-minute meeting this week to discuss Q1 planning? Thursday 2pm or Friday 10am work for me. Thanks, John"
}

print("="*80)
print("CONVERSATIONAL AI TEST SUITE")
print("="*80)

# Test 1: Intent Detection
print("\n1. INTENT DETECTION TESTS")
print("-"*80)

test_messages = [
    ("send it", "SEND_COMMAND"),
    ("looks good, send", "SEND_COMMAND"),
    ("ignore this", "NO_RESPONSE"),
    ("no response needed", "NO_RESPONSE"),
    ("what's this about?", "QUESTION"),
    ("who sent this?", "QUESTION"),
    ("draft a reply", "DRAFT_REQUEST"),
    ("make it friendlier", "REFINEMENT"),
]

for message, expected in test_messages:
    intent = ai.determine_intent(message, email_context, has_draft=(expected=="REFINEMENT"))
    status = "✅" if intent == expected else "❌"
    print(f"{status} '{message}' → {intent} (expected: {expected})")

# Test 2: Conversational Responses
print("\n\n2. CONVERSATIONAL RESPONSE TESTS")
print("-"*80)

questions = [
    "What's this email about?",
    "Who is John Smith?",
    "Is this urgent?",
    "Should I respond to this?"
]

for question in questions:
    print(f"\nQ: {question}")
    response = ai.chat_with_supervisor(question, email_context, [])
    print(f"A: {response}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
