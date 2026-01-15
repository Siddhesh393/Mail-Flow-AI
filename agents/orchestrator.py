import json

from config.sheets import get_sheet
from config.settings import load_settings
from agents.composer import compose_reply
from utils.time import now_iso
from utils.human_check import looks_like_human_email


def run_orchestrator(limit: int = 5):
    sheet = get_sheet()
    inbox_ws = sheet.worksheet("inbox_queue")
    drafts_ws = sheet.worksheet("drafts")

    rows = inbox_ws.get_all_records()
    processed = 0

    for idx, row in enumerate(rows, start=2):  # header row = 1
        if processed >= limit:
            break

        if row.get("status") != "NEW":
            continue

        # 🔒 Lock row
        inbox_ws.update_cell(idx, 7, "PROCESSING")

        body = (row.get("body") or "").strip()
        if not body:
            inbox_ws.update_cell(idx, 7, "SKIPPED")
            inbox_ws.update_cell(idx, 8, "empty_body")
            continue

        # 🧠 Load headers for human detection
        try:
            headers = json.loads(row.get("headers", "{}"))
        except Exception:
            headers = {}

        is_human = looks_like_human_email(
            from_email=row.get("from_email", ""),
            body=body,
            headers=headers
        )

        if not is_human:
            inbox_ws.update_cell(idx, 7, "SKIPPED")
            inbox_ws.update_cell(idx, 8, "non_human")
            continue

        # 🤖 Compose reply
        result = compose_reply(
            from_email=row.get("from_email", ""),
            subject=row.get("subject", ""),
            body=body
        )

        drafts_ws.append_row([
            row.get("email_id"),
            result["draft"],
            result["tone"],
            result["confidence"],
            "DRAFT",  # 👈 explicit default
            now_iso()
        ])

        inbox_ws.update_cell(idx, 8, result["intent"])
        inbox_ws.update_cell(idx, 9, result["confidence"])
        inbox_ws.update_cell(idx, 7, "DONE")

        processed += 1


def run_auto_sender(limit: int = 5):
    settings = load_settings()
    threshold = float(settings.get("confidence_threshold", 1.0))

    sheet = get_sheet()
    inbox_ws = sheet.worksheet("inbox_queue")
    drafts_ws = sheet.worksheet("drafts")
    sent_ws = sheet.worksheet("sent_log")

    inbox = inbox_ws.get_all_records()
    drafts = drafts_ws.get_all_records()
    sent_ids = {row["email_id"] for row in sent_ws.get_all_records()}

    inbox_map = {row["email_id"]: row for row in inbox}

    processed = 0

    for draft in drafts:
        if processed >= limit:
            break

        # ✅ ONLY SEND WHEN EXPLICITLY COMMANDED
        if draft.get("approved") != "SEND":
            continue

        email_id = draft["email_id"]

        if email_id in sent_ids:
            continue

        if float(draft["confidence"]) < threshold:
            continue

        inbox_row = inbox_map.get(email_id)
        if not inbox_row:
            continue

        try:
            from agents.email_sender import send_reply

            send_reply(
                thread_id=inbox_row["thread_id"],
                to_email=inbox_row["from_email"],
                subject=inbox_row["subject"],
                body=draft["draft_body"]
            )

            sent_ws.append_row([
                email_id,
                now_iso(),
                True,
                ""
            ])

            processed += 1

        except Exception as e:
            sent_ws.append_row([
                email_id,
                now_iso(),
                False,
                str(e)
            ])
