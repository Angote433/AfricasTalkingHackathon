"""
document_ingestion.py
---------------------
Drop-in ingestion layer for the fraud detection backend.
Converts PDF / DOCX / image files into PIL Images that your
existing fraud pipeline already knows how to handle.

Usage (FastAPI example):

    from document_ingestion import ingest_upload

    @app.post("/analyze")
    async def analyze(file: UploadFile = File(...)):
        images = await ingest_upload(file)
        results = [fraud_pipeline(img) for img in images]
        return results
"""

import io
import os
import tempfile
from pathlib import Path
from typing import List

from PIL import Image


# ── optional heavy deps (imported lazily so missing ones give clear errors) ──

def _require(package: str, install_hint: str):
    import importlib
    try:
        return importlib.import_module(package)
    except ImportError:
        raise ImportError(
            f"Missing dependency '{package}'. "
            f"Install it with:  pip install {install_hint}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Core converters
# ─────────────────────────────────────────────────────────────────────────────

def pdf_to_images(file_bytes: bytes, dpi: int = 150) -> List[Image.Image]:
    pdf2image = _require("pdf2image", "pdf2image poppler-utils")
    convert = pdf2image.convert_from_bytes

    POPPLER_PATH = r"C:\Users\arnol\OneDrive\Desktop\poppler\poppler-26.02.0\Library\bin" 

    pages = convert(file_bytes, dpi=dpi, fmt="png", poppler_path=POPPLER_PATH)
    return pages

def docx_to_images(file_bytes: bytes, dpi: int = 150) -> List[Image.Image]:
    """
    Convert a DOCX to images by:
      1. DOCX → PDF  (via docx2pdf, requires LibreOffice on Linux)
      2. PDF  → images
    Falls back to extracting embedded images if conversion fails.
    """
    try:
        docx2pdf = _require("docx2pdf", "docx2pdf")
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = os.path.join(tmpdir, "input.docx")
            pdf_path  = os.path.join(tmpdir, "output.pdf")
            with open(docx_path, "wb") as f:
                f.write(file_bytes)
            docx2pdf.convert(docx_path, pdf_path)
            with open(pdf_path, "rb") as f:
                return pdf_to_images(f.read(), dpi=dpi)
    except Exception:
        # Fallback: pull embedded images straight from the DOCX (zip archive)
        return _extract_images_from_docx(file_bytes)


def _extract_images_from_docx(file_bytes: bytes) -> List[Image.Image]:
    import zipfile
    images = []
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        for name in z.namelist():
            if name.startswith("word/media/"):
                with z.open(name) as img_file:
                    try:
                        img = Image.open(img_file).convert("RGB")
                        images.append(img.copy())
                    except Exception:
                        pass
    return images


def image_to_pil(file_bytes: bytes) -> List[Image.Image]:
    """Wrap a raw image (JPEG/PNG/BMP/WEBP) in a list for uniform handling."""
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return [img]


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

SUPPORTED = {
    ".pdf":  pdf_to_images,
    ".docx": docx_to_images,
    ".doc":  docx_to_images,
    ".jpg":  image_to_pil,
    ".jpeg": image_to_pil,
    ".png":  image_to_pil,
    ".bmp":  image_to_pil,
    ".webp": image_to_pil,
}


def ingest_file(file_bytes: bytes, filename: str, dpi: int = 150) -> List[Image.Image]:
    """
    Convert any supported file format to a list of PIL Images.

    Args:
        file_bytes: raw bytes of the uploaded file
        filename:   original filename (used to detect extension)
        dpi:        resolution for PDF/DOCX rasterisation

    Returns:
        list of PIL.Image.Image  (one per page/image)

    Raises:
        ValueError: if the file extension is not supported
    """
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Supported: {', '.join(SUPPORTED.keys())}"
        )
    converter = SUPPORTED[ext]
    # image converters don't need dpi param
    if ext in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
        return converter(file_bytes)
    return converter(file_bytes, dpi=dpi)


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI async wrapper  (use this in your router)
# ─────────────────────────────────────────────────────────────────────────────

async def ingest_upload(upload_file, dpi: int = 150) -> List[Image.Image]:
    """
    Accepts a FastAPI UploadFile object and returns PIL Images.

    Example:
        @app.post("/analyze")
        async def analyze(file: UploadFile = File(...)):
            images  = await ingest_upload(file)
            results = [your_fraud_model(img) for img in images]
            return {"pages": len(images), "results": results}
    """
    file_bytes = await upload_file.read()
    return ingest_file(file_bytes, upload_file.filename, dpi=dpi)


# ─────────────────────────────────────────────────────────────────────────────
# Quick test  (python document_ingestion.py path/to/receipt.pdf)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python document_ingestion.py <path_to_file>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "rb") as f:
        raw = f.read()

    pages = ingest_file(raw, path)
    print(f"\n✓ Loaded '{path}'  →  {len(pages)} page(s)")
    for i, img in enumerate(pages, 1):
        print(f"  Page {i}: {img.size[0]}×{img.size[1]} px, mode={img.mode}")

    # Save previews
    for i, img in enumerate(pages, 1):
        out = f"preview_page_{i}.png"
        img.save(out)
        print(f"  Saved preview → {out}")
