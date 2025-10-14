from typing import Dict, Optional

TEAM_MAP = {
    "password": "ServiceDesk",
    "vpn": "Network",
    "email_outlook": "Messaging",
    "printer": "EndUserSupport",
    "network": "Network",
    "hardware": "EndUserSupport",
    "software": "Apps",
    "access_request": "Identity",
    "other": "ServiceDesk"
}

def priority_from(context_category: str, urgency: Optional[str], confidence: Optional[float]) -> str:
    if urgency:
        u = urgency.lower()
        if u in ["critical", "p1"]: return "P1"
        if u in ["high", "p2"]: return "P2"
        if u in ["medium", "p3"]: return "P3"
        return "P4"

    if context_category in ["network", "vpn"] and (confidence or 0) >= 0.7:
        return "P2"
    if context_category in ["password", "email_outlook"]:
        return "P3"
    return "P4"

def route_ticket(category: str, urgency: Optional[str], confidence: Optional[float]) -> Dict:
    team = TEAM_MAP.get(category, "ServiceDesk")
    priority = priority_from(category, urgency, confidence)
    return {"team": team, "priority": priority}