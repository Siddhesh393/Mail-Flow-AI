import json
import os

from dotenv import load_dotenv
from google import genai

from config.settings import load_settings

load_dotenv()

# Initialize Gemini client (NEW SDK STYLE)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def call_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "temperature": 0.4,
            "response_mime_type": "application/json"
        }
    )

    return response.text.strip()


def compose_reply(from_email: str, subject: str, body: str) -> dict:
    settings = load_settings()

    sender_name = settings.get("sender_name", "Siddhesh")
    tone = settings.get("default_tone", "polite")
    availability = settings.get("default_availability", "")
    signature = settings.get("email_signature", f"Best regards,\n{sender_name}")

    blocked_keywords = settings.get("block_keywords", [])

    body_lower = body.lower()

    # 🔒 Safety gate: blocked keywords
    if any(word in body_lower for word in blocked_keywords):
        return {
            "draft": "",
            "tone": tone,
            "intent": "blocked",
            "confidence": 0.0
        }

    prompt = f"""
You are an autonomous email assistant writing on behalf of {sender_name}.

STRICT RULES (NO EXCEPTIONS):
- Do NOT ask questions that require human input.
- Do NOT use placeholders or brackets of any kind.
- Do NOT say "please let me know" or "feel free to".
- Make reasonable assumptions and proceed confidently.
- If a meeting is mentioned, propose concrete availability directly.
- Always produce a complete, ready-to-send email.
- Always sign with the exact signature provided.

Tone: {tone}

Default availability (use when scheduling is implied):
{availability}

Signature (MUST USE EXACTLY):
{signature}

EMAIL TO RESPOND TO:
From: {from_email}
Subject: {subject}
Body:
{body}

OUTPUT REQUIREMENTS:
- Respond ONLY in valid JSON
- No markdown
- No explanations

JSON format:
{{
  "draft": "...",
  "intent": "...",
  "confidence": 0.0
}}
"""


    try:
        raw_output = call_gemini(prompt)
        data = json.loads(raw_output)
    except Exception:
        return {
            "draft": "",
            "tone": tone,
            "intent": "parse_error",
            "confidence": 0.0
        }

    return {
        "draft": data.get("draft", ""),
        "tone": tone,
        "intent": data.get("intent", "unknown"),
        "confidence": float(data.get("confidence", 0.0))
    }
