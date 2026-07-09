"""
at_service.py
-------------
Africa's Talking integration for MediClaim AI.
Handles SMS alerts and OTP verification.

SMS is sent via a direct HTTPS POST to the Africa's Talking sandbox API
rather than the africastalking SDK. On this machine the SDK's HTTPS calls
fail with SSL: WRONG_VERSION_NUMBER (local antivirus SSL inspection
intercepting Python's HTTPS traffic); the dedicated session below disables
certificate verification to work around that. This session is used only
within this module — never import or share it elsewhere.

Config:
  Set AT_USERNAME and AT_API_KEY in environment variables,
  or in backend/.env (loaded via load_dotenv() in main.py).

  For sandbox testing:
    AT_USERNAME = "sandbox"
    AT_API_KEY  = your sandbox key from account.africastalking.com
"""

import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── Config ────────────────────────────────────────────────────────────────────
AT_USERNAME = os.getenv("AT_USERNAME")
AT_API_KEY  = os.getenv("AT_API_KEY")

# Sandbox only — swap to https://api.africastalking.com/version1/messaging for production
AT_SMS_URL = "https://api.sandbox.africastalking.com/version1/messaging"

# Dedicated session for Africa's Talking calls only. Verification is disabled
# to work around local SSL interception — do not reuse this session for
# anything else.
_session = requests.Session()
_session.verify = False


def _post_sms(message: str, recipients: list) -> dict:
    """POST an SMS send request directly to the AT sandbox API."""
    response = _session.post(
        AT_SMS_URL,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "apiKey": AT_API_KEY,
        },
        data={
            "username": AT_USERNAME,
            "to": ",".join(recipients),
            "message": message,
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_phone(phone: str) -> str:
    """
    Normalize phone to international format for AT.
    Handles: 07XXXXXXXX, 7XXXXXXXX, +2547XXXXXXXX, 2547XXXXXXXX
    """
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        return phone
    if phone.startswith("07") or phone.startswith("01"):
        return "+254" + phone[1:]
    if phone.startswith("7") or phone.startswith("1"):
        return "+254" + phone
    if phone.startswith("254"):
        return "+" + phone
    return phone


def _risk_emoji(risk: str) -> str:
    return {"LOW": "✅", "MEDIUM": "⚠️", "HIGH": "🚨", "CRITICAL": "❌"}.get(risk, "")


# ── OTP ───────────────────────────────────────────────────────────────────────

def send_otp(phone: str, otp_code: str) -> dict:
    """Send an OTP SMS to the given phone number."""
    try:
        formatted = _format_phone(phone)
        message = (
            f"MediClaim AI\n"
            f"Your verification code is: {otp_code}\n"
            f"Valid for 5 minutes. Do not share this code."
        )
        response = _post_sms(message, [formatted])
        recipients = response.get("SMSMessageData", {}).get("Recipients", [])
        success = any(r.get("status") == "Success" for r in recipients)
        return {
            "success": success,
            "phone": formatted,
            "response": response,
        }
    except Exception as e:
        print(f"[AT] OTP SMS failed: {e}")
        return {"success": False, "error": str(e)}


# ── Claim status SMS ──────────────────────────────────────────────────────────

def send_claim_received(phone: str, claim_id: str) -> dict:
    """SMS sent immediately when a claim is submitted."""
    try:
        formatted = _format_phone(phone)
        short_id  = claim_id[:8].upper()
        message = (
            f"MediClaim AI\n"
            f"Claim #{short_id} received.\n"
            f"We are analyzing your document now.\n"
            f"You will receive the result shortly."
        )
        response = _post_sms(message, [formatted])
        return {"success": True, "response": response}
    except Exception as e:
        print(f"[AT] Claim received SMS failed: {e}")
        return {"success": False, "error": str(e)}


def send_claim_result(phone: str, claim_id: str, analysis: dict) -> dict:
    """SMS sent when fraud analysis is complete."""
    try:
        formatted    = _format_phone(phone)
        short_id     = claim_id[:8].upper()
        score        = analysis.get("fraud_score", 0)
        risk         = analysis.get("risk_category", "UNKNOWN")
        action       = analysis.get("recommendation", "REVIEW")
        emoji        = _risk_emoji(risk)
        hospital     = analysis.get("extracted_data", {}).get("hospital_name", "Unknown")
        total        = analysis.get("extracted_data", {}).get("total_amount")
        total_str    = f"KES {total:,.0f}" if total else "N/A"

        # Build red flags summary (max 2 for SMS brevity)
        flags     = analysis.get("red_flags", [])
        flag_lines = ""
        if flags:
            top = flags[:2]
            flag_lines = "\nFlags:\n" + "\n".join(f"- {f.get('description','')}" for f in top)

        message = (
            f"MediClaim AI {emoji}\n"
            f"Claim #{short_id}\n"
            f"Hospital: {hospital}\n"
            f"Amount: {total_str}\n"
            f"Risk: {risk} ({score:.0f}/100)"
            f"{flag_lines}\n"
            f"Action: {action}\n"
            f"Reply STATUS {short_id} for full report."
        )
        response = _post_sms(message, [formatted])
        return {"success": True, "response": response}
    except Exception as e:
        print(f"[AT] Claim result SMS failed: {e}")
        return {"success": False, "error": str(e)}


def send_fraud_investigator_alert(phone: str, claim_id: str, analysis: dict) -> dict:
    """
    High-priority SMS to investigator/supervisor when score ≥ 80.
    Use your fraud team's number here in production.
    """
    try:
        formatted = _format_phone(phone)
        short_id  = claim_id[:8].upper()
        score     = analysis.get("fraud_score", 0)
        hospital  = analysis.get("extracted_data", {}).get("hospital_name", "Unknown")
        flags     = analysis.get("red_flags", [])
        top_flag  = flags[0].get("description", "See report") if flags else "See report"

        message = (
            f"⚠️ FRAUD ALERT — MediClaim AI\n"
            f"Claim #{short_id}\n"
            f"Score: {score:.0f}/100 — CRITICAL\n"
            f"Hospital: {hospital}\n"
            f"Top flag: {top_flag}\n"
            f"Immediate investigation required."
        )
        response = _post_sms(message, [formatted])
        return {"success": True, "response": response}
    except Exception as e:
        print(f"[AT] Investigator alert SMS failed: {e}")
        return {"success": False, "error": str(e)}


def send_status_update(phone: str, claim_id: str, status: str) -> dict:
    """SMS when a reviewer manually updates a claim status."""
    try:
        formatted = _format_phone(phone)
        short_id  = claim_id[:8].upper()
        messages  = {
            "APPROVED":      f"✅ Claim #{short_id} has been APPROVED.\nPayment will be processed shortly.",
            "REJECTED":      f"❌ Claim #{short_id} has been REJECTED.\nContact your insurer for details.",
            "INVESTIGATING": f"🔍 Claim #{short_id} is under investigation.\nAn officer will contact you within 48hrs.",
            "REVIEW":        f"📋 Claim #{short_id} has been sent for further review.\nWe will update you shortly.",
        }
        message = messages.get(status.upper(), f"Claim #{short_id} status: {status}")
        response = _post_sms(message, [formatted])
        return {"success": True, "response": response}
    except Exception as e:
        print(f"[AT] Status update SMS failed: {e}")
        return {"success": False, "error": str(e)}
