from agents.email_io import fetch_unread_emails
from agents.orchestrator import run_orchestrator, run_auto_sender


def main():
    print("📥 Fetching unread emails...")
    fetch_unread_emails(max_results=5)

    print("🧠 Generating drafts with Gemini...")
    run_orchestrator(limit=5)

    print("📤 Sending approved replies...")
    run_auto_sender(limit=5)

    print("✅ MailFlow AI cycle completed")


if __name__ == "__main__":
    main()
