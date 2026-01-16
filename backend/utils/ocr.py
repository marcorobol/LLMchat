import io
from PIL import Image
import pytesseract

def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extracts text from image bytes using OCR.
    Requires tesseract-ocr installed on system.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"OCR Error: {e}")
        return "[Error extracting text from image]"
