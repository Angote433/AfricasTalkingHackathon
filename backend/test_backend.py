print("Testing imports...")

try:
    print("1. Importing FastAPI...")
    from fastapi import FastAPI
    print("   ✓ FastAPI imported")
except Exception as e:
    print(f"   ✗ FastAPI error: {e}")

try:
    print("2. Importing PIL...")
    from PIL import Image
    print("   ✓ PIL imported")
except Exception as e:
    print(f"   ✗ PIL error: {e}")

try:
    print("3. Importing OpenCV...")
    import cv2
    print("   ✓ OpenCV imported")
except Exception as e:
    print(f"   ✗ OpenCV error: {e}")

try:
    print("4. Importing pytesseract...")
    import pytesseract
    print("   ✓ pytesseract imported")
except Exception as e:
    print(f"   ✗ pytesseract error: {e}")

try:
    print("5. Importing ocr_service...")
    import ocr_service
    print("   ✓ ocr_service imported")
except Exception as e:
    print(f"   ✗ ocr_service error: {e}")

try:
    print("6. Importing forensics_service...")
    import forensics_service
    print("   ✓ forensics_service imported")
except Exception as e:
    print(f"   ✗ forensics_service error: {e}")

try:
    print("7. Importing cost_service...")
    import cost_service
    print("   ✓ cost_service imported")
except Exception as e:
    print(f"   ✗ cost_service error: {e}")

try:
    print("8. Importing business_rules...")
    import business_rules
    print("   ✓ business_rules imported")
except Exception as e:
    print(f"   ✗ business_rules error: {e}")

try:
    print("9. Importing fraud_scoring...")
    import fraud_scoring
    print("   ✓ fraud_scoring imported")
except Exception as e:
    print(f"   ✗ fraud_scoring error: {e}")

print("\n✓ All imports successful!")