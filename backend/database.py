import sqlite3
import uuid
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
 
DB_PATH = Path(__file__).parent / "mediclaim.db"
 
 
def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn
 
 
def init_db():
    """Create tables if they don't exist. Call once on startup."""
    conn = get_connection()
    c = conn.cursor()
 
    # Claims table
    c.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            id              TEXT PRIMARY KEY,
            phone_number    TEXT NOT NULL,
            filename        TEXT,
            fraud_score     REAL,
            risk_category   TEXT,
            recommendation  TEXT,
            red_flags       TEXT,     -- JSON string
            total_amount    REAL,
            hospital_name   TEXT,
            invoice_number  TEXT,
            invoice_date    TEXT,
            image_url       TEXT,
            ela_image_url   TEXT,
            status          TEXT DEFAULT 'PENDING',
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        )
    """)
 
    # OTP table
    c.execute("""
        CREATE TABLE IF NOT EXISTS otps (
            id          TEXT PRIMARY KEY,
            phone       TEXT NOT NULL,
            code        TEXT NOT NULL,
            expires_at  TEXT NOT NULL,
            used        INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
 
    conn.commit()
    conn.close()
    print("✓ Database initialized at", DB_PATH)
 
 
# ── Claims ────────────────────────────────────────────────────────────────────
 
def save_claim(claim_id: str, phone_number: str, analysis: dict) -> dict:
    """Persist a completed claim analysis."""
    import json
    conn = get_connection()
    c = conn.cursor()
 
    extracted = analysis.get("extracted_data", {})
    red_flags  = json.dumps(analysis.get("red_flags", []))
 
    c.execute("""
        INSERT INTO claims (
            id, phone_number, filename, fraud_score, risk_category,
            recommendation, red_flags, total_amount, hospital_name,
            invoice_number, invoice_date, image_url, ela_image_url, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        claim_id,
        phone_number,
        analysis.get("file_type", ""),
        analysis.get("fraud_score"),
        analysis.get("risk_category"),
        analysis.get("recommendation"),
        red_flags,
        extracted.get("total_amount"),
        extracted.get("hospital_name"),
        extracted.get("invoice_number"),
        extracted.get("invoice_date"),
        analysis.get("image_url"),
        analysis.get("ela_image_url"),
        "ANALYZED",
    ))
    conn.commit()
    conn.close()
    return get_claim(claim_id)
 
 
def get_claim(claim_id: str) -> dict | None:
    """Fetch a single claim by ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM claims WHERE id = ?", (claim_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None
 
 
def get_all_claims(limit: int = 50) -> list:
    """Fetch recent claims for the dashboard."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM claims ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]
 
 
def update_claim_status(claim_id: str, status: str):
    """Update claim status (APPROVED / REJECTED / INVESTIGATING)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE claims
        SET status = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (status, claim_id))
    conn.commit()
    conn.close()
 
 
# ── OTP ───────────────────────────────────────────────────────────────────────
 
def generate_otp(phone: str, expiry_minutes: int = 5) -> str:
    """Generate and store a 6-digit OTP for the given phone number."""
    code       = "".join(random.choices(string.digits, k=6))
    otp_id     = str(uuid.uuid4())
    expires_at = (datetime.now() + timedelta(minutes=expiry_minutes)).isoformat()
 
    conn = get_connection()
    c = conn.cursor()
 
    # Invalidate any existing unused OTPs for this phone
    c.execute("UPDATE otps SET used = 1 WHERE phone = ? AND used = 0", (phone,))
 
    c.execute("""
        INSERT INTO otps (id, phone, code, expires_at)
        VALUES (?, ?, ?, ?)
    """, (otp_id, phone, code, expires_at))
    conn.commit()
    conn.close()
    return code
 
 
def verify_otp(phone: str, code: str) -> tuple[bool, str]:
    """
    Verify an OTP code for a phone number.
    Returns (success: bool, message: str)
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM otps
        WHERE phone = ? AND code = ? AND used = 0
        ORDER BY created_at DESC LIMIT 1
    """, (phone, code))
    row = c.fetchone()
 
    if not row:
        conn.close()
        return False, "Invalid OTP code"
 
    expires_at = datetime.fromisoformat(row["expires_at"])
    if datetime.now() > expires_at:
        conn.close()
        return False, "OTP has expired. Please request a new one."
 
    # Mark as used
    c.execute("UPDATE otps SET used = 1 WHERE id = ?", (row["id"],))
    conn.commit()
    conn.close()
    return True, "OTP verified successfully"