import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Create credentials.json dynamically if it doesn't exist
                if not os.path.exists('credentials.json'):
                    self._create_credentials_file()
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                # Manual console flow since run_console is deprecated/removed
                flow.redirect_uri = 'http://localhost'
                auth_url, _ = flow.authorization_url(prompt='consent')
                
                print('\n\nPlease go to this URL:\n{}\n\n'.format(auth_url))
                code = input('Enter the authorization code: ')
                flow.fetch_token(code=code)
                self.creds = flow.credentials
            
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)

    def _create_credentials_file(self):
        import json
        client_config = {
            "installed": {
                "client_id": os.getenv("GMAIL_CLIENT_ID"),
                "project_id": "project-aura", # Placeholder, not strictly needed for auth flow if client_id/secret are correct
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
                "redirect_uris": ["http://localhost"]
            }
        }
        with open('credentials.json', 'w') as f:
            json.dump(client_config, f)

    def list_unread_emails(self):
        results = self.service.users().messages().list(userId='me', q='is:unread').execute()
        messages = results.get('messages', [])
        return messages

    def get_email_content(self, msg_id):
        message = self.service.users().messages().get(userId='me', id=msg_id).execute()
        payload = message['payload']
        headers = payload.get("headers")
        subject = next(h['value'] for h in headers if h['name'] == 'Subject')
        sender = next(h['value'] for h in headers if h['name'] == 'From')
        
        parts = payload.get('parts')
        body = ""
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode()
                    break
        else:
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode()
            
        return {
            "id": msg_id,
            "subject": subject,
            "sender": sender,
            "body": body
        }

    def send_email(self, to, subject, body):
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message = {'raw': raw}
        self.service.users().messages().send(userId='me', body=message).execute()

    def mark_as_read(self, msg_id):
        self.service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
