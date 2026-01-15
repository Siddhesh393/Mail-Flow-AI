import os
import base64
import json
from email.utils import parsedate_to_datetime

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from config.sheets import get_sheet

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_FILE = "token.json"


def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "gmail_credentials.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0)

        # 💾 Save token for reuse
        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def extract_body(payload):
    if "data" in payload.get("body", {}):
        return base64.urlsafe_b64decode(
            payload["body"]["data"]
        ).decode("utf-8", errors="ignore")

    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            return base64.urlsafe_b64decode(
                part["body"]["data"]
            ).decode("utf-8", errors="ignore")

    return ""


def fetch_unread_emails(max_results=10):
    service = get_gmail_service()
    sheet = get_sheet()
    inbox_ws = sheet.worksheet("inbox_queue")

    existing_ids = {
        row["email_id"]
        for row in inbox_ws.get_all_records()
        if row.get("email_id")
    }

    results = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])

    for msg in messages:
        msg_id = msg["id"]
        if msg_id in existing_ids:
            continue

        message = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

        headers = {
            h["name"]: h["value"]
            for h in message["payload"]["headers"]
        }

        inbox_ws.append_row([
            msg_id,
            message["threadId"],
            headers.get("From", ""),
            headers.get("Subject", ""),
            extract_body(message["payload"]),
            parsedate_to_datetime(headers.get("Date")).isoformat(),
            "NEW",
            "",
            "",
            json.dumps(headers)
        ])


        # Mark as read
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
