import re

# --- HARD SIGNALS (EMAIL PROTOCOL LEVEL) ---

AUTOMATION_HEADERS = [
    "List-Unsubscribe",
    "List-Id",
    "Auto-Submitted",
    "Precedence",
    "X-Auto-Response-Suppress",
    "X-Campaign",
    "X-Mailer",
    "X-Mandrill-User",
    "X-Mailgun-Sid",
    "X-Sendgrid-Id"
]

PRECEDENCE_VALUES = {"bulk", "list", "junk"}

NO_REPLY_PATTERNS = [
    r"no[-_]?reply",
    r"donotreply",
    r"do[-_]?not[-_]?reply",
    r"mailer-daemon",
    r"bounce",
    r"automated"
]

# --- CONTENT SIGNALS ---

MARKETING_PHRASES = [
    "unsubscribe",
    "view in browser",
    "manage preferences",
    "email preferences",
    "privacy policy",
    "terms of service",
    "you are receiving this email",
    "this email was sent to"
]

CTA_PATTERNS = [
    r"click here",
    r"learn more",
    r"get started",
    r"buy now",
    r"sign up",
    r"read more"
]

URL_REGEX = re.compile(r"https?://")


def looks_like_no_reply(from_email: str) -> bool:
    email = from_email.lower()
    return any(re.search(p, email) for p in NO_REPLY_PATTERNS)


def has_bulk_headers(headers: dict) -> bool:
    for h in AUTOMATION_HEADERS:
        if h in headers:
            return True

    precedence = headers.get("Precedence", "").lower()
    if precedence in PRECEDENCE_VALUES:
        return True

    auto_submitted = headers.get("Auto-Submitted", "").lower()
    if auto_submitted and auto_submitted != "no":
        return True

    return False


def looks_like_marketing(body: str) -> bool:
    body_lower = body.lower()
    phrase_hits = sum(1 for p in MARKETING_PHRASES if p in body_lower)
    return phrase_hits >= 2


def looks_like_bulk_cta(body: str) -> bool:
    body_lower = body.lower()
    cta_hits = sum(1 for p in CTA_PATTERNS if re.search(p, body_lower))
    url_count = len(URL_REGEX.findall(body_lower))
    return cta_hits >= 1 and url_count >= 2


def structural_bot_score(body: str) -> int:
    """
    Score-based approach instead of yes/no.
    Higher score = more likely automated.
    """
    score = 0
    body_lower = body.lower()

    if len(body.split()) > 250:
        score += 1

    if looks_like_marketing(body):
        score += 2

    if looks_like_bulk_cta(body):
        score += 2

    if body.count("\n") > 15:
        score += 1

    return score


def looks_like_human_email(from_email: str, body: str, headers: dict) -> bool:
    # 1️⃣ Hard blocks
    if looks_like_no_reply(from_email):
        return False

    if has_bulk_headers(headers):
        return False

    # 2️⃣ Structural scoring
    bot_score = structural_bot_score(body)

    # Threshold tuned from real inbox behavior
    if bot_score >= 3:
        return False

    # 3️⃣ Very short messages are often automated pings
    if len(body.split()) < 3:
        return False

    return True
