import os
import shutil
import subprocess
import sys
from ocr_service import extract_text_from_image


def tesseract_info():
    env = os.environ.get('TESSERACT_CMD') or os.environ.get('TESSERACT_PATH')
    which = shutil.which('tesseract')
    print('TESSERACT_CMD env:', env)
    print('tesseract on PATH:', which)
    if which:
        try:
            out = subprocess.check_output([which, '--version'], stderr=subprocess.STDOUT, text=True)
            print('\n--- tesseract --version ---')
            print(out.splitlines()[0])
        except Exception as e:
            print('Failed to run tesseract --version:', e)


def run_ocr_test(image_path):
    print('\nRunning OCR on:', image_path)
    try:
        text = extract_text_from_image(image_path)
        print('\n--- OCR Result (first 800 chars) ---')
        print(text[:800])
    except Exception as e:
        print('OCR failed with exception:')
        import traceback
        traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        print('Usage: python test_ocr.py <image_path>')
        sys.exit(1)

    image_path = sys.argv[1]
    tesseract_info()
    run_ocr_test(image_path)


if __name__ == '__main__':
    main()
