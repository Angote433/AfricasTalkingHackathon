"""
Image Forensics Service - Detect Digital Manipulation
Performs EXIF analysis, screenshot detection, and Error Level Analysis (ELA)
"""

import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import os
import tempfile

# Try importing OpenCV; if it fails (e.g., NumPy ABI mismatch), disable ELA and continue
try:
    import cv2
    HAS_CV2 = True
    _cv2_import_error = None
except Exception as e:
    cv2 = None
    HAS_CV2 = False
    _cv2_import_error = str(e)


def extract_exif_data(image_path):
    """
    Extract EXIF metadata from image
    """
    try:
        image = Image.open(image_path)
        exif_data = {}
        
        info = image._getexif()
        
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                # Convert bytes to string if needed
                if isinstance(value, bytes):
                    try:
                        value = value.decode()
                    except:
                        value = str(value)
                exif_data[decoded] = value
        
        return exif_data
    except Exception as e:
        print(f"EXIF extraction error: {str(e)}")
        return {}


def detect_editing_software(exif_data):
    """
    Check if image was edited with image editing software
    """
    editing_tools = [
        'photoshop', 'gimp', 'paint.net', 'pixelmator', 
        'affinity', 'lightroom', 'snapseed', 'vsco',
        'adobe', 'corel', 'paintshop'
    ]
    
    software = exif_data.get('Software', '')
    if software:
        software_lower = software.lower()
        for tool in editing_tools:
            if tool in software_lower:
                return True, software
    
    return False, None


def is_screenshot(exif_data, filename):
    """
    Detect if image is a screenshot
    """
    # Check filename patterns
    screenshot_patterns = [
        'screenshot', 'screen shot', 'screen_shot',
        'capture', 'screen_', 'snap_', 'img_'
    ]
    
    filename_lower = filename.lower()
    for pattern in screenshot_patterns:
        if pattern in filename_lower:
            return True
    
    # Screenshots often lack EXIF data
    if not exif_data or len(exif_data) < 5:
        return True
    
    # Check for screenshot software
    software = exif_data.get('Software', '').lower()
    if any(word in software for word in ['screenshot', 'snipping', 'capture']):
        return True
    
    return False


def perform_ela(image_path, quality=95):
    """
    Perform Error Level Analysis to detect image manipulation
    Returns ELA image and manipulation score
    """
    if not HAS_CV2:
        print("ELA skipped: OpenCV (cv2) not available:", _cv2_import_error)
        return None, 0

    try:
        # Open with PIL and ensure RGB
        original = Image.open(image_path)
        if original.mode != 'RGB':
            original = original.convert('RGB')

        # Write a temporary compressed copy (safe temp file)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        tmp_path = tmp_file.name
        tmp_file.close()
        try:
            original.save(tmp_path, 'JPEG', quality=quality)

            # Read both images with OpenCV
            original_cv = cv2.imread(str(image_path))
            compressed_cv = cv2.imread(tmp_path)

            if original_cv is None or compressed_cv is None:
                raise RuntimeError('OpenCV failed to read image(s) for ELA')

            # Calculate difference and amplify
            diff = cv2.absdiff(original_cv, compressed_cv)
            ela_image = diff.astype('float32') * 10.0
            ela_image = np.clip(ela_image, 0, 255).astype('uint8')

            # Calculate manipulation score (average difference)
            manipulation_score = float(np.mean(diff))

            # Save ELA image next to original with _ela suffix
            base, _ = os.path.splitext(image_path)
            ela_output_path = f"{base}_ela.jpg"
            cv2.imwrite(ela_output_path, ela_image)

            return ela_output_path, manipulation_score
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
    
    except Exception as e:
        print(f"ELA error: {str(e)}")
        return None, 0


def calculate_manipulation_score(exif_data, ela_score, is_screenshot_flag):
    """
    Calculate overall manipulation score (0-100)
    """
    score = 0
    
    # EXIF checks (40 points max)
    edited, software = detect_editing_software(exif_data)
    if edited:
        score += 40
    
    # Screenshot check (20 points)
    if is_screenshot_flag:
        score += 20
    
    # ELA score (40 points max)
    # Normalize ELA score: typical manipulation shows >10 mean difference
    normalized_ela = min(ela_score / 10 * 40, 40)
    score += normalized_ela
    
    return min(score, 100)


def analyze_image_authenticity(image_path, filename):
    """
    Main function to analyze image for manipulation
    """
    try:
        # Extract EXIF data
        exif_data = extract_exif_data(image_path)
        
        # Check for editing software
        edited, software_used = detect_editing_software(exif_data)
        
        # Check if screenshot
        is_screenshot_flag = is_screenshot(exif_data, filename)
        
        # Perform ELA
        ela_image_path, ela_score = perform_ela(image_path)
        
        # Calculate manipulation score
        manipulation_score = calculate_manipulation_score(
            exif_data, ela_score, is_screenshot_flag
        )
        
        # Determine if manipulation detected
        manipulation_detected = manipulation_score > 30
        
        return {
            'success': True,
            'exif_data': {
                'software': exif_data.get('Software', 'Unknown'),
                'device': exif_data.get('Model', 'Unknown'),
                'created_date': exif_data.get('DateTime', 'Unknown'),
                'edited_with_software': edited,
                'software_used': software_used
            },
            'is_screenshot': is_screenshot_flag,
            'ela_image_path': ela_image_path,
            'ela_score': float(ela_score),
            'manipulation_score': float(manipulation_score),
            'manipulation_detected': manipulation_detected
        }
    
    except Exception as e:
        print(f"Forensics analysis error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }