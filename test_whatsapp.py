from dotenv import load_dotenv
import os

load_dotenv()

from services.whatsapp_service import WhatsAppService

whatsapp = WhatsAppService()

try:
    supervisor = os.getenv("SUPERVISOR_WHATSAPP")
    print(f"Sending test message to: {supervisor}")
    message_sid = whatsapp.send_message(supervisor, "🧪 Test message from Aura Agent")
    print(f"✅ Message sent successfully! SID: {message_sid}")
except Exception as e:
    print(f"❌ Error sending message: {e}")
    import traceback
    traceback.print_exc()
