"""
MediClaim AI - Main FastAPI Application
Automated Medical Receipt Fraud Detection System
"""
 
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
from pathlib import Path
import uuid
import io
from fastapi import Request

# Import services
from document_ingestion import ingest_file
from ocr_service import extract_receipt_info
from forensics_service import analyze_image_authenticity
from forensics_service import HAS_CV2, _cv2_import_error
from cost_service import validate_costs
from business_rules import validate_business_rules
import fraud_scoring
import database
import at_service
 
# Initialize FastAPI app
app = FastAPI(
    title="MediClaim AI",
    description="Automated Medical Receipt Fraud Detection System",
    version="1.0.0"
)
 
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# Create uploads directory (absolute path relative to project)
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
 
# Mount uploads directory for serving images
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Initialize database tables
database.init_db()


# ── Request models ───────────────────────────────────────────────────────────
class OtpSendRequest(BaseModel):
    phone: str


class OtpVerifyRequest(BaseModel):
    phone: str
    code: str


class LoginRequest(BaseModel):
    phone: str
    code: str


class StatusUpdateRequest(BaseModel):
    status: str


def _get_officer_phone(authorization: str | None) -> str:
    """Validate the Authorization Bearer token and return the logged-in officer's phone."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    session = database.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Please log in again.")
    return session["phone"]
 
 
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MediClaim AI API",
        "version": "1.0.0",
        "status": "running"
    }
 
 
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
 
 
SUPPORTED_TYPES = [
    "image/jpeg", "image/jpg", "image/png", "image/bmp", "image/webp",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
]
@app.post("/api/debug")
async def debug_upload(request: Request):
    body = await request.body()
    print("Content-Type:", request.headers.get("content-type"))
    print("Body length:", len(body))
    print("Body preview:", body[:200])
    return {"content_type": request.headers.get("content-type"), "body_length": len(body)}
 
@app.post("/api/analyze")
async def analyze_receipt(
    file: UploadFile = File(...),
    patient_phone: str = Form(None),
    authorization: str = Header(None),
):
    officer_phone = _get_officer_phone(authorization)

    print("=== INCOMING REQUEST ===")
    print("Filename:", file.filename)
    print("Content type:", file.content_type)
    print("Officer:", officer_phone)
    print("========================")
    """
    Main endpoint to analyze uploaded receipt.
    Supports JPEG, PNG, PDF, DOCX.
 
    Process:
    1. Save uploaded file
    2. Convert to image (if PDF/DOCX)
    3. Extract text (OCR)
    4. Analyze image authenticity (forensics)
    5. Validate costs
    6. Apply business rules
    7. Calculate fraud score
    8. Return comprehensive analysis
    """
 
    try:
        # Validate file type
        if file.content_type not in SUPPORTED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Unsupported file type '{file.content_type}'. "
                    "Please upload JPEG, PNG, PDF, or DOCX."
                )
            )
 
        # Generate unique claim ID
        claim_id = str(uuid.uuid4())
 
        # Read raw bytes once
        file_bytes = await file.read()
 
        # ── Convert any format → PIL images ──────────────────────────────────
        try:
            pil_images = ingest_file(file_bytes, file.filename)
        except Exception as conv_err:
            raise HTTPException(
                status_code=422,
                detail=f"Could not convert file to image: {conv_err}"
            )
 
        # Use first page for analysis (multi-page support can be added later)
        pil_image = pil_images[0]
 
        # Save the (possibly converted) image to disk so existing services work
        filename = f"{claim_id}.png"
        file_path = UPLOAD_DIR / filename
        pil_image.save(str(file_path), "PNG")
 
        # Also save the original file for reference
        orig_ext  = file.filename.rsplit(".", 1)[-1].lower()
        orig_name = f"{claim_id}_original.{orig_ext}"
        orig_path = UPLOAD_DIR / orig_name
        with open(orig_path, "wb") as f_orig:
            f_orig.write(file_bytes)
        
        print(f"Processing claim: {claim_id} | pages: {len(pil_images)} | saved as PNG")
 
        # Step 1: OCR - Extract text
        print("Step 1: Extracting text...")
        ocr_result = extract_receipt_info(str(file_path))
        
        if not ocr_result['success']:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract text from image. Please upload a clearer photo."
            )
        
        extracted_data = ocr_result['data']
        print(f"  Extracted: {extracted_data['hospital_name']}, ${extracted_data['total_amount']}")
        
        # Step 2: Forensics - Analyze image authenticity
        print("Step 2: Analyzing image authenticity...")
        forensics_result = analyze_image_authenticity(str(file_path), file.filename)
        
        if not forensics_result['success']:
            print(f"  Warning: Forensics analysis failed: {forensics_result.get('error')}")
            forensics_result = {
                'manipulation_score': 0,
                'is_screenshot': False,
                'exif_data': {},
                'ela_image_path': None
            }
        else:
            print(f"  Manipulation score: {forensics_result['manipulation_score']:.1f}")
        
        # Step 3: Cost validation
        print("Step 3: Validating costs...")
        cost_validation = validate_costs(extracted_data.get('line_items', []))
        print(f"  Flagged items: {cost_validation['flagged_items']}")
        
        # Step 4: Business rules
        print("Step 4: Applying business rules...")
        business_rules_result = validate_business_rules(extracted_data)
        print(f"  Rule violations: {len(business_rules_result['violations'])}")
        
        # Step 5: Compile final analysis
        print("Step 5: Calculating fraud score...")
        final_report = fraud_scoring.compile_final_analysis(
            extracted_data,
            forensics_result,
            cost_validation,
            business_rules_result
        )
        
        final_report['claim_id']   = claim_id
        final_report['image_url']  = f"/uploads/{filename}"
        final_report['page_count'] = len(pil_images)
        final_report['file_type']  = orig_ext
        
        if forensics_result.get('ela_image_path'):
            ela_filename = os.path.basename(forensics_result['ela_image_path'])
            final_report['ela_image_url'] = f"/uploads/{ela_filename}"
        
        print(f"✓ Analysis complete! Fraud score: {final_report['fraud_score']}")

        # Persist the claim so it can be looked up later (e.g. for status-update SMS).
        # phone_number is the PATIENT's number — that's who gets notified of the decision,
        # not the officer who logged in. Fall back to the officer's phone if no patient number given.
        notify_phone = patient_phone or officer_phone
        if notify_phone:
            try:
                database.save_claim(claim_id, notify_phone, final_report)
            except Exception as db_err:
                print(f"[DB] Failed to save claim {claim_id}: {db_err}")
        else:
            print(f"[DB] No phone provided for claim {claim_id}, skipping persistence")

        return {
            "success": True,
            "data": final_report
        }
    
    except HTTPException as he:
        raise he
    
    except Exception as e:
        print(f"Error analyzing receipt: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error_code": "PROCESSING_FAILED",
            "message": "An error occurred while processing the receipt",
            "detail": str(e)
        }
 
 
@app.get("/api/claims/{claim_id}")
async def get_claim(claim_id: str):
    """
    Retrieve claim analysis results
    (For demo purposes, this would query a database in production)
    """
    return {
        "success": False,
        "message": "Claim retrieval not implemented in MVP"
    }


VALID_CLAIM_STATUSES = {"APPROVED", "REVIEW", "INVESTIGATING", "REJECTED"}


@app.patch("/api/claims/{claim_id}/status")
async def update_claim_status_endpoint(claim_id: str, payload: StatusUpdateRequest):
    """
    Officer decision on a claim. Persists the new status and SMSes the patient.
    """
    status = payload.status.strip().upper()
    if status not in VALID_CLAIM_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{payload.status}'. Must be one of {sorted(VALID_CLAIM_STATUSES)}."
        )

    claim = database.get_claim(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    database.update_claim_status(claim_id, status)

    sms_result = at_service.send_status_update(claim["phone_number"], claim_id, status)
    if not sms_result.get("success"):
        print(f"[AT] Status SMS failed for claim {claim_id}: {sms_result.get('error')}")

    return {
        "success": True,
        "claim_id": claim_id,
        "status": status,
        "sms_sent": bool(sms_result.get("success")),
    }


@app.post("/api/auth/login")
async def login(payload: LoginRequest):
    """
    Verify an officer's OTP and start a session (valid 8 hours).
    Replaces per-claim OTP verification — the officer logs in once per shift.
    """
    success, message = database.verify_otp(payload.phone, payload.code)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    token = database.create_session(payload.phone)
    return {"success": True, "token": token, "phone": payload.phone}


@app.get("/api/auth/validate")
async def validate_session(authorization: str = Header(None)):
    """Check whether a session token is still valid."""
    phone = _get_officer_phone(authorization)
    return {"valid": True, "phone": phone}


@app.post("/api/auth/logout")
async def logout(authorization: str = Header(None)):
    """Invalidate a session token (end of shift)."""
    if authorization and authorization.startswith("Bearer "):
        database.delete_session(authorization.removeprefix("Bearer ").strip())
    return {"success": True}


@app.post("/api/otp/send")
async def send_otp_endpoint(payload: OtpSendRequest):
    """Generate an OTP for the given phone number and SMS it via Africa's Talking."""
    if not payload.phone.strip():
        raise HTTPException(status_code=400, detail="Phone number is required")

    code = database.generate_otp(payload.phone)
    result = at_service.send_otp(payload.phone, code)

    if not result.get("success") and at_service.AT_USERNAME != "sandbox":
        raise HTTPException(status_code=502, detail="Failed to send OTP SMS. Please try again.")

    response = {"success": True}
    if at_service.AT_USERNAME == "sandbox":
        # Surface the code in sandbox mode only, since sandbox SMS may not be deliverable
        response["debug_code"] = code
    return response


@app.post("/api/otp/verify")
async def verify_otp_endpoint(payload: OtpVerifyRequest):
    """Verify an OTP code previously sent to a phone number."""
    success, message = database.verify_otp(payload.phone, payload.code)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}
 
 
if __name__ == "__main__":
    print("=" * 60)
    print("MediClaim AI - Fraud Detection System")
    print("=" * 60)
    print("Starting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
 
    # Startup diagnostics (printed after server stops)
    if not HAS_CV2:
        print("WARNING: OpenCV (cv2) is not available or failed to import:")
        print(_cv2_import_error)
        print("If you see NumPy ABI errors, run: pip install 'numpy<2' --force-reinstall")