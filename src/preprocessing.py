import cv2
import numpy as np
from PIL import Image

def preprocess_image(image: Image.Image, method: str = "none") -> Image.Image:
    """
    Apply preprocessing to improve OCR accuracy.
    Methods: 'none', 'grayscale', 'threshold', 'denoise'
    """
    img = np.array(image.convert("RGB"))
    
    if method == "none":
        return image
    
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    if method == "grayscale":
        return Image.fromarray(gray)
    elif method == "threshold":
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return Image.fromarray(thresh)
    elif method == "denoise":
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        return Image.fromarray(denoised)
    else:
        raise ValueError(f"Unknown preprocessing method: {method}") 