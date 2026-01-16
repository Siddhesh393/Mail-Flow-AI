import base64
from email.message import EmailMessage

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from config.sheets import get_sheet
from utils.time import now_iso

TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build("gmail", "v1", credentials=creds)


def send_reply(
    thread_id: str,
    message_id: str,
    to_email: str,
    subject: str,
    body: str
):
    service = get_gmail_service()

    # 📧 Construct proper reply email
    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = f"Re: {subject}"
    msg["In-Reply-To"] = message_id
    msg["References"] = message_id

    msg.set_content(body)

    encoded_message = base64.urlsafe_b64encode(
        msg.as_bytes()
    ).decode("utf-8")

    # 📤 Send email (preserves thread)
    service.users().messages().send(
        userId="me",
        body={
            "raw": encoded_message,
            "threadId": thread_id
        }
    ).execute()

    # 📊 Update Google Sheet (reply status)
    sheet = get_sheet()
    ws = sheet.worksheet("inbox_queue")

    records = ws.get_all_records()

    for idx, row in enumerate(records, start=2):  # sheet row index
        if row.get("thread_id") == thread_id:
            ws.update_cell(idx, 7, "REPLIED")          # status
            ws.update_cell(idx, 8, now_iso())          # reply time
            break
