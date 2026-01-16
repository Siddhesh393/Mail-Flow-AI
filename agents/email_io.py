import os
import base64
import json
from email.utils import parsedate_to_datetime

from googleapiclient.discovery import build
from utils.google_auth import get_credentials
from config.sheets import get_sheet

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "gmail_credentials.json"

MAX_CELL_CHARS = 45000  # keep buffer below 50k

def truncate(text: str, limit: int = MAX_CELL_CHARS) -> str:
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n[TRUNCATED]"


def get_gmail_service():
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


def extract_body(payload):
    """Recursively extract text/plain email body"""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    for part in payload.get("parts", []):
        text = extract_body(part)
        if text:
            return text

    return ""


def safe_parse_date(date_str):
    try:
        return parsedate_to_datetime(date_str).isoformat()
    except Exception:
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
    fetched_emails = []

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

        email_data = {
            "email_id": msg_id,
            "thread_id": message["threadId"],
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "body": extract_body(message["payload"]),
            "received_time": safe_parse_date(headers.get("Date")),
            "status": "NEW",
            "headers": headers
        }

        inbox_ws.append_row([
            email_data["email_id"],
            email_data["thread_id"],
            email_data["from"],
            email_data["subject"],
            truncate(email_data["body"]),                 
            email_data["received_time"],
            email_data["status"],
            "",
            "",
            truncate(json.dumps(headers))                  
        ])


        fetched_emails.append(email_data)

        # Mark email as read
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()

    return fetched_emails
