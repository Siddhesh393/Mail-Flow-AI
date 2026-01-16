# 📧 MailFlow AI 🤖  
*A Confidence-Based Autonomous Email Agent*

MailFlow AI is an **agentic email automation system** that reads incoming Gmail messages, filters out non-human emails, drafts **complete and confident replies using Google Gemini**, and **automatically sends replies only when the model is sufficiently confident**.

The system is designed to be:
- **Autonomous** (no placeholders, no follow-up questions)
- **Safe** (confidence-gated autosend)
- **Transparent** (Google Sheets as the source of truth)

---

## ✨ Key Features

### 📥 Gmail Inbox Ingestion
- Reads unread emails via **Gmail API**
- Deduplicates emails using message IDs
- Stores inbox state in Google Sheets

### 🧠 Human-Only Detection
- Filters newsletters, system emails, bots, and promotions
- Uses header patterns + structural heuristics
- Ensures replies are only drafted for real human emails

### ✍️ AI Email Drafting (Gemini)
- Uses **Google Gemini (latest SDK)**
- Produces **complete, ready-to-send replies**
- No placeholders like `[Your Name]`
- No “please suggest…” questions
- Always signs emails correctly

### 🚀 Confidence-Based Autosend
- Each draft includes a confidence score
- Emails are auto-sent **only if confidence ≥ threshold**
- Low-confidence drafts are retained for review

### 📊 Google Sheets as State & Audit Log
- `inbox_queue` → ingestion & filtering
- `drafts` → drafted replies + confidence
- `sent_log` → delivery status

---

## 🧠 System Architecture

```text
Gmail Inbox
   ↓
Email Ingestion Agent
   ↓
Google Sheets (inbox_queue)
   ↓
Orchestrator Agent
├─ Human Email Filter
├─ Gemini Composer
├─ Confidence Gate
   ↓
Google Sheets (drafts)
   ↓ (confidence ≥ threshold)
Auto Sender Agent
   ↓
Gmail Reply
   ↓
Google Sheets (sent_log)
```

## 🧰 Tech Stack

- **Python 3.10+**
- **Google Gemini API** (LLM)
- **Gmail API** (OAuth)
- **Google Sheets API** (Service Account)
- **Google Drive API**


---


## 📁 Project Structure

```text
MailFlow AI/
├── agents/
│   ├── composer.py          # Gemini-powered email drafting
│   ├── email_io.py          # Gmail inbox ingestion
│   ├── email_sender.py      # Gmail reply sender
│   └── orchestrator.py      # Main control agent
│
├── config/
│   ├── config.example.json  # Safe, versioned config template
│   ├── settings.py          # Config loader
│   └── sheets.py            # Sheets access layer
│
├── utils/
│   ├── google_auth.py       # Central OAuth handler (Gmail + Sheets)
│   ├── human_check.py       # Human email detection
│   └── time.py              # Timestamp utilities
│
├── main.py                  # Entry point
├── requirements.txt
├── README.md
└── .gitignore

```
## 🔐 Files Not Included

For security reasons, the following files are **intentionally NOT included** in this repository.  
You must create or download them locally for the project to work.

These files contain secrets or runtime credentials and are ignored via `.gitignore`:

- `.env`  
  Stores environment variables (e.g., API keys)

- `gmail_credentials.json`  
  Google OAuth 2.0 client credentials (downloaded from Google Cloud Console)

- `token.json`  
  OAuth access & refresh tokens (auto-generated on first run)

- `config/config.json`  
  Local configuration file with personal details and thresholds

---