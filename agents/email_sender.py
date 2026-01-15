from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64

from config.sheets import get_sheet
from utils.time import now_iso

TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build("gmail", "v1", credentials=creds)


def send_reply(thread_id, to_email, subject, body):
    service = get_gmail_service()

    message_text = f"""To: {to_email}
Subject: Re: {subject}

{body}
"""

    encoded_message = base64.urlsafe_b64encode(
        message_text.encode("utf-8")
    ).decode("utf-8")

    service.users().messages().send(
        userId="me",
        body={
            "raw": encoded_message,
            "threadId": thread_id
        }
    ).execute()
