from agents.email_io import fetch_unread_emails
from agents.orchestrator import run_orchestrator, run_auto_sender

if __name__ == "__main__":
    # Phase 1: Gmail → Google Sheets
    fetch_unread_emails(max_results=20)

    # Phase 2: Generate drafts
    run_orchestrator()

    # Phase 3: Auto-send (if enabled)
    run_auto_sender()
