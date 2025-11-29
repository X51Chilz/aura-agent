from services.gmail_service import GmailService
from dotenv import load_dotenv

load_dotenv()

print("Attempting to authenticate with Gmail...")
service = GmailService()
print("Authentication successful!")

print("Listing unread emails...")
emails = service.list_unread_emails()
print(f"Found {len(emails)} unread emails.")
