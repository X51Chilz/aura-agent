# Aura Agent - AI Email Assistant

An intelligent email assistant that monitors Gmail, summarizes incoming emails, and helps you craft responses through WhatsApp conversations.

## Features

- 📧 **Gmail Integration**: Monitors inbox for new emails
- 🤖 **AI-Powered Summarization**: Uses OpenAI to summarize emails
- 💬 **WhatsApp Notifications**: Sends email summaries to your WhatsApp
- ✍️ **Collaborative Response Drafting**: Chat with AI to craft the perfect response
- 📤 **Automated Sending**: Approve and send emails directly from WhatsApp

## Architecture

- **FastAPI**: Web framework for webhook handling
- **Gmail API**: Email monitoring and sending
- **OpenAI API**: Email summarization and response generation
- **Twilio**: WhatsApp messaging
- **SQLite**: Conversation state management

## Setup

### Prerequisites

- Python 3.12+
- Gmail account with API access
- OpenAI API key
- Twilio account with WhatsApp enabled
- Domain with HTTPS (for webhook)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd aura_agent
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Set up Gmail OAuth:
   - Create a Desktop App OAuth Client ID in Google Cloud Console
   - Enable Gmail API
   - Run the application and complete authentication

6. Configure Twilio webhook:
   - Set webhook URL to: `https://your-domain.com/webhook/whatsapp`
   - Method: POST

### Running

```bash
python3 main.py
```

The application will:
- Start on port 8000
- Begin monitoring Gmail every 60 seconds
- Listen for WhatsApp messages via webhook

## Usage

1. **Receive Email**: When a new email arrives, you'll get a WhatsApp message with a summary
2. **Draft Response**: Reply with instructions like "Draft a friendly response"
3. **Refine**: Continue chatting to refine the response
4. **Send**: Reply "send it" to approve and send the email

## Project Structure

```
aura_agent/
├── main.py                 # FastAPI application
├── services/
│   ├── gmail_service.py    # Gmail API integration
│   ├── ai_service.py       # OpenAI integration
│   └── whatsapp_service.py # Twilio WhatsApp integration
├── utils/
│   └── db.py              # SQLite database
├── requirements.txt
└── .env
```

## License

MIT
