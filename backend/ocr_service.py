"""
OCR Service - Text Extraction from Medical Receipts
Uses Tesseract OCR to extract text and parse key fields
"""

import re
from datetime import datetime
from dateutil import parser as date_parser
import pytesseract
from PIL import Image
import os
import shutil


def _configure_tesseract():
    """Try to find the Tesseract executable and configure pytesseract.

    Resolution order:
    1. `TESSERACT_CMD` env var (full path to executable)
    2. `shutil.which('tesseract')` (on PATH)
    3. common Windows install locations
    If none found, leave unset — OCR functions will raise a clear error.
    """
    # 1) Environment override
    env_path = os.environ.get('TESSERACT_CMD') or os.environ.get('TESSERACT_PATH')
    if env_path:
        if os.path.exists(env_path):
            pytesseract.pytesseract.tesseract_cmd = env_path
            return

    # 2) On PATH
    which_path = shutil.which('tesseract')
    if which_path:
        pytesseract.pytesseract.tesseract_cmd = which_path
        return

    # 3) Common Windows locations
    if os.name == 'nt':
        candidates = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        for c in candidates:
            if os.path.exists(c):
                pytesseract.pytesseract.tesseract_cmd = c
                return


# configure at import time (best-effort)
_configure_tesseract()


def extract_text_from_image(image_path):
    """
    Extract raw text from image using Tesseract OCR
    """
    try:
        # Ensure tesseract binary is available
        tcmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', None)
        found = shutil.which('tesseract') or (tcmd and os.path.exists(tcmd))
        if not found:
            raise RuntimeError(
                "Tesseract executable not found.\n"
                "Install Tesseract OCR (https://github.com/tesseract-ocr/tesseract) and ensure it's on your PATH,\n"
                "or set the environment variable TESSERACT_CMD to the full path of tesseract executable."
            )
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        # Re-raise with helpful message for missing tesseract vs general OCR failures
        if isinstance(e, RuntimeError):
            raise
        raise Exception("Failed to extract text from image: " + str(e))


def parse_receipt_data(raw_text):
    """
    Parse extracted text to identify key fields
    """
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    
    extracted_data = {
        'hospital_name': extract_hospital_name(lines),
        'invoice_number': extract_invoice_number(raw_text),
        'invoice_date': extract_date(raw_text),
        'total_amount': extract_total_amount(raw_text),
        'line_items': extract_line_items(lines)
    }
    
    return extracted_data


def extract_hospital_name(lines):
    """
    Extract hospital name (usually in first 2-3 lines)
    """
    if not lines:
        return None
    
    # Take first non-empty line as hospital name
    for line in lines[:5]:
        if len(line) > 5 and not line.isdigit():
            # Clean up the name
            name = re.sub(r'[^a-zA-Z0-9\s&,-]', '', line)
            if len(name) > 5:
                return name.strip()
    
    return lines[0] if lines else None


def extract_invoice_number(text):
    """
    Extract invoice/receipt number using pattern matching
    """
    patterns = [
        r'(?:invoice|receipt|bill)\s*(?:no|number|#)[\s:]*([A-Z0-9-]+)',
        r'(?:INV|REC|BILL)[\s-]*([A-Z0-9-]+)',
        r'#\s*([A-Z0-9-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def extract_date(text):
    """
    Extract date — only from lines that actually contain date keywords.
    Avoids picking up ages, invoice numbers, or other stray numbers.
    """
    # Only look for dates on lines containing date-related keywords
    date_keywords = re.compile(r'\b(date|dated|invoice date|receipt date|visit date)\b', re.IGNORECASE)
    date_patterns = [
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',           # 2026-03-24
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',          # 24/03/2026
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
    ]

    # First pass: only lines with date keywords
    for line in text.split('\n'):
        if date_keywords.search(line):
            for pattern in date_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        parsed = date_parser.parse(match.group(), fuzzy=True)
                        # Sanity check — must be between 2000 and today
                        if 2000 <= parsed.year <= datetime.now().year:
                            return parsed.strftime('%Y-%m-%d')
                    except:
                        continue

    # Second pass: any line with a clear date pattern (no keyword required)
    for pattern in date_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                parsed = date_parser.parse(match.group(), fuzzy=True)
                if 2000 <= parsed.year <= datetime.now().year:
                    return parsed.strftime('%Y-%m-%d')
            except:
                continue

    return None


def extract_total_amount(text):
    """
    Extract total amount. Priority: GRAND TOTAL > SUBTOTAL > TOTAL AMOUNT > TOTAL.
    Explicitly skips lines containing age, patient, policy, receipt no, phone.
    """
    # Lines to skip — these contain numbers that are NOT amounts
    skip_pattern = re.compile(
        r'\b(age|patient|policy|receipt\s*no|invoice\s*no|phone|tel|p\.?o\.?\s*box|'
        r'attending|doctor|dr\.?|ref|reg|id)\b',
        re.IGNORECASE
    )

    # Ordered by priority — grand total is most reliable
    priority_patterns = [
        r'grand\s+total[\s:KES$]*([\d,]+(?:\.\d{1,2})?)',
        r'total\s+amount[\s:KES$]*([\d,]+(?:\.\d{1,2})?)',
        r'net\s+amount[\s:KES$]*([\d,]+(?:\.\d{1,2})?)',
        r'amount\s+due[\s:KES$]*([\d,]+(?:\.\d{1,2})?)',
        r'subtotal[\s:KES$]*([\d,]+(?:\.\d{1,2})?)',
        r'\btotal[\s:KES$]*([\d,]+(?:\.\d{1,2})?)',
    ]

    for pattern in priority_patterns:
        for line in text.split('\n'):
            if skip_pattern.search(line):
                continue
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    amount = float(match.group(1).replace(',', ''))
                    if amount >= 100:   # ignore amounts < KES 100 (likely noise)
                        return amount
                except:
                    continue

    return None


# Words that indicate a line is metadata, NOT a billable service
_META_SKIP = re.compile(
    r'\b(patient|age|sex|gender|policy|receipt\s*no|invoice\s*no|receipt\s*number|'
    r'attending|doctor|dr\.?|date|phone|tel|p\.?o\.?\s*box|address|email|'
    r'subtotal|sub\s*total|grand\s*total|total|vat|tax|discount|balance|'
    r'itemised|itemized|description|qty|quantity|unit\s*price|amount)\b',
    re.IGNORECASE
)

# KES prefix pattern (our receipts use "KES 1,880")
_KES_AMOUNT = re.compile(r'(?:KES|KSH|Ksh)[\s]*([\d,]+(?:\.\d{1,2})?)', re.IGNORECASE)
_TRAILING_AMOUNT = re.compile(r'^(.+?)\s+([\d,]{3,}(?:\.\d{1,2})?)$')


def extract_line_items(lines):
    """
    Extract billable line items only.
    - Skips metadata lines (patient name, age, date, totals, headers)
    - Handles 'Description  Qty  Unit Price  Total' table rows
    - Handles 'KES X,XXX' format
    - Min amount KES 100, max KES 500,000
    """
    line_items = []
    in_itemised_section = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect start of itemised section
        if re.search(r'\b(itemised\s*bill|itemized\s*bill|services?\s*rendered|bill\s*details)\b', line, re.IGNORECASE):
            in_itemised_section = True
            continue

        # Stop at totals section
        if re.search(r'\b(subtotal|sub\s*total|grand\s*total|total\s*amount|vat|tax)\b', line, re.IGNORECASE):
            continue

        # Skip pure metadata lines
        if _META_SKIP.search(line):
            continue

        # Skip very short lines (headers, row numbers)
        if len(line) < 6:
            continue

        price = None
        description = None

        # Pattern 1: "Description  1  1,880  1,880" (table with qty+unit+total)
        # Take last number as the line total
        table_match = re.match(r'^(\d+\s+)?(.+?)\s+\d+\s+([\d,]+)\s+([\d,]+)$', line)
        if table_match:
            description = table_match.group(2).strip()
            try:
                price = float(table_match.group(4).replace(',', ''))
            except:
                pass

        # Pattern 2: "Service name   KES 1,880"
        if price is None:
            kes_match = _KES_AMOUNT.search(line)
            if kes_match:
                try:
                    price = float(kes_match.group(1).replace(',', ''))
                    description = line[:kes_match.start()].strip()
                    # Clean leading row numbers e.g. "1 Red Blood Cell Count"
                    description = re.sub(r'^\d+\s+', '', description).strip()
                except:
                    pass

        # Pattern 3: "Some description    2,339" (trailing number ≥ 3 digits)
        if price is None:
            trail_match = _TRAILING_AMOUNT.match(line)
            if trail_match:
                try:
                    price = float(trail_match.group(2).replace(',', ''))
                    description = trail_match.group(1).strip()
                    description = re.sub(r'^\d+\s+', '', description).strip()
                except:
                    pass

        if description and price is not None:
            # Final guards
            if len(description) < 4:
                continue
            if not (100 <= price <= 500_000):
                continue
            # Skip if description still looks like metadata
            if _META_SKIP.search(description):
                continue

            line_items.append({'description': description, 'price': price})

    # Deduplicate and cap at 10
    seen = set()
    unique = []
    for item in line_items:
        key = item['description'].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique[:10]




def extract_text_from_pdf_native(file_path):
    """
    Extract text directly from a PDF using pdfplumber (no OCR needed).
    Falls back to Tesseract if pdfplumber not installed or PDF is scanned.
    """
    try:
        import pdfplumber
        text_pages = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_pages.append(t)
        combined = "\n".join(text_pages).strip()
        if len(combined) > 50:   # meaningful text found
            return combined
    except ImportError:
        pass
    except Exception as e:
        print(f"pdfplumber failed ({e}), falling back to OCR")

    # Fallback: convert PDF page to image then OCR
    return None


def extract_receipt_info(image_path):
    """
    Main function. For PDFs, tries native text extraction first.
    """
    try:
        path_lower = str(image_path).lower()
        raw_text = None

        if path_lower.endswith('.pdf'):
            raw_text = extract_text_from_pdf_native(image_path)

        if not raw_text:
            raw_text = extract_text_from_image(image_path)

        extracted_data = parse_receipt_data(raw_text)
        return {
            'success': True,
            'data': extracted_data,
            'raw_text': raw_text
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
