from typing import Dict

CATEGORIES = ["password", "vpn", "email_outlook", "printer", "network", "hardware", "software", "access_request", "other"]

RULES = {
    "password": ["password", "passcode", "login failed", "locked account", "forgot"],
    "vpn": ["vpn", "remote", "anyconnect", "forticlient", "mfa"],
    "email_outlook": ["outlook", "email", "mailbox", "office 365", "o365"],
    "printer": ["printer", "print", "toner", "paper jam", "jam"],
    "network": ["network", "wifi", "internet", "lan", "wan", "proxy", "dns"],
    "hardware": ["laptop", "desktop", "mouse", "keyboard", "hardware"],
    "software": ["install", "application", "software", "update", "license"],
    "access_request": ["access", "permission", "authorization", "role", "entitlement"]
}

def classify_by_rules(text: str) -> Dict:
    t = (text or "").lower()
    scores = {}
    for cat, keys in RULES.items():
        score = sum(1 for k in keys if k in t)
        if score > 0:
            scores[cat] = score
    if not scores:
        return {"category": "other", "confidence": 0.3}
    category = max(scores, key=scores.get)
    conf = min(0.9, 0.4 + 0.1 * scores[category])
    return {"category": category, "confidence": conf}

def classify_text(text: str) -> Dict:
    return classify_by_rules(text)