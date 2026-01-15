import json
import requests

from config.settings import load_settings

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:latest"  # change if needed


def call_llama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    response.raise_for_status()
    return response.json()["response"]


def compose_reply(from_email: str, subject: str, body: str) -> dict:
    settings = load_settings()

    tone = settings.get("default_tone", "polite")
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
You are an intelligent email assistant.

Your task:
1. Understand the email
2. Identify the intent
3. Write a reply in a {tone} tone
4. Estimate confidence (0.0 to 1.0)

EMAIL:
From: {from_email}
Subject: {subject}
Body:
{body}

IMPORTANT:
Respond ONLY in valid JSON.
Do NOT add explanations.
Do NOT wrap in markdown.

JSON format:
{{
  "draft": "...",
  "intent": "...",
  "confidence": 0.0
}}
"""

    raw_output = call_llama(prompt).strip()

    try:
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
        "confidence": float(data.get("confidence", 0))
    }
