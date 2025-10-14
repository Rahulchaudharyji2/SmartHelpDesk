import os
import time
import imaplib
import email
import requests
from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USER = os.getenv("IMAP_USER")
IMAP_PASS = os.getenv("IMAP_PASS")
IMAP_MAILBOX = os.getenv("IMAP_MAILBOX", "INBOX")
POLL_SECONDS = int(os.getenv("IMAP_POLL_SECONDS", "30"))

API_BASE = f"http://{os.getenv('HOST','0.0.0.0')}:{os.getenv('PORT','8000')}"
INGEST_URL = f"{API_BASE}/tickets/ingest"

def connect():
    M = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    M.login(IMAP_USER, IMAP_PASS)
    M.select(IMAP_MAILBOX)
    return M

def parse_message(raw_bytes):
    msg = email.message_from_bytes(raw_bytes)
    subject_hdr = msg.get("Subject", "")
    decoded = email.header.decode_header(subject_hdr)
    subject = ""
    for part, enc in decoded:
        if isinstance(part, bytes):
            subject += part.decode(enc or "utf-8", errors="ignore")
        else:
            subject += part or ""
    from_addr = email.utils.parseaddr(msg.get("From", ""))[1]

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disp = str(part.get("Content-Disposition"))
            if ctype == "text/plain" and "attachment" not in (disp or "").lower():
                payload = part.get_payload(decode=True) or b""
                body = payload.decode(errors="ignore")
                break
    else:
        payload = msg.get_payload(decode=True) or b""
        body = payload.decode(errors="ignore")

    return subject or "(no subject)", body.strip(), from_addr

def ingest_email(subject, body, sender, uid):
    data = {
        "subject": subject,
        "body": body,
        "user_email": sender,
        "channel": "email",
        "source_ref": f"imap:{uid}"
    }
    try:
        r = requests.post(INGEST_URL, json=data, timeout=10)
        r.raise_for_status()
        print(f"[IMAP] Ingested UID {uid}: {subject}")
        return True
    except Exception as e:
        print(f"[IMAP] Failed to ingest UID {uid}: {e}")
        return False

def main():
    if not all([IMAP_HOST, IMAP_USER, IMAP_PASS]):
        print("[IMAP] Missing IMAP configuration in .env; exiting.")
        return
    while True:
        try:
            M = connect()
            typ, data = M.search(None, 'UNSEEN')
            if typ != "OK":
                raise RuntimeError("IMAP search failed")
            uids = data[0].split()
            for uid in uids:
                typ, msg_data = M.fetch(uid, '(RFC822)')
                if typ != "OK":
                    continue
                raw = msg_data[0][1]
                subject, body, sender = parse_message(raw)
                ok = ingest_email(subject, body, sender, uid.decode())
                if ok:
                    M.store(uid, '+FLAGS', '\\Seen')
            M.logout()
        except Exception as e:
            print(f"[IMAP] Error: {e}")
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()