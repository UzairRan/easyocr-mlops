import easyocr
import numpy as np
from PIL import Image
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

class OCREngine:
    def __init__(self, languages=None, gpu=None):
        self.languages = languages or config["ocr"]["languages"]
        self.gpu = gpu if gpu is not None else config["ocr"]["gpu"]
        self.reader = easyocr.Reader(self.languages, gpu=self.gpu)

    def extract_text(self, image: Image.Image) -> str:
        """Run OCR on a PIL Image and return extracted text."""
        img_array = np.array(image)
        result = self.reader.readtext(img_array, detail=0, paragraph=True)
        return "\n".join(result)

    def extract_with_confidence(self, image: Image.Image):
        """Return list of (text, confidence) for each detected block."""
        img_array = np.array(image)
        result = self.reader.readtext(img_array, detail=1, paragraph=False)
        return [(res[1], res[2]) for res in result]  # (text, confidence)

# Singleton instance for FastAPI to avoid reloading
_ocr_instance = None

def get_ocr_engine():
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = OCREngine()
    return _ocr_instance 