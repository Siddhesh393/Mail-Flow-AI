# Mail Flow AI 🤖📧

Mail Flow AI is a **human-only, agentic email assistant** that reads incoming Gmail messages, detects whether they were written by real humans, drafts intelligent replies using a **local LLaMA model**, and sends responses **only when explicitly approved**.

This project is designed with **safety, control, and transparency** in mind — no blind auto-replies.

---

## ✨ Features

- 📥 **Gmail Inbox Ingestion**
  - Reads unread emails via Gmail API
  - Deduplicates and stores state in Google Sheets

- 🧠 **Human-only Detection**
  - Filters out newsletters, bots, system emails, and marketing
  - Uses email headers + structural heuristics
  - Optional LLaMA arbitration for edge cases

- ✍️ **AI Drafting (Local LLaMA)**
  - Uses Ollama + LLaMA (no paid APIs)
  - Configurable tone and safety keywords
  - Outputs confidence score per draft

- 🧾 **Human-in-the-loop Approval**
  - Drafts are stored in Google Sheets
  - Emails are sent **only when approved = `SEND`**
  - No accidental replies

- 📊 **Google Sheets as State & Audit Log**
  - Inbox queue
  - Drafts
  - Sent log

---

## 🧠 Architecture Overview

```text 
Gmail Inbox
↓
Email Ingestion Agent
↓
Google Sheets (inbox_queue)
↓
Orchestrator Agent
├─ Human Detection
├─ LLaMA Composer
↓
Google Sheets (drafts)
↓ (approved = SEND)
Auto Sender Agent
↓
Gmail Reply
↓
Google Sheets (sent_log)
```

---

## 🧰 Tech Stack

- **Python 3.10+**
- **Gmail API** (OAuth)
- **Google Sheets API** (Service Account)
- **Ollama + LLaMA 3.x**
- **gspread**
- **requests**

---

## 📁 Project Structure

```text
Mail Flow AI/
├── agents/
│ ├── composer.py
│ ├── orchestrator.py
│ ├── email_io.py
│ └── email_sender.py
│
├── config/
│ ├── config.json
│ ├── settings.py
│ └── sheets.py
│
├── utils/
│ ├── human_check.py
│ └── time.py
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```
