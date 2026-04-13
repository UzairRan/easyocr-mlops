import time
from fastapi import FastAPI, UploadFile, File # type: ignore
from PIL import Image
import io

from src.ocr_engine import get_ocr_engine
from src.preprocessing import preprocess_image
from app.schemas import OCRResponse
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

app = FastAPI(title="General OCR API", version="1.0.0")
engine = get_ocr_engine()

@app.post("/ocr", response_model=OCRResponse)
async def ocr_endpoint(file: UploadFile = File(...), preprocess: str = "none"):
    start_time = time.time()
    
    # Read image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Preprocess
    processed = preprocess_image(image, preprocess)
    
    # Extract text and confidence blocks
    text = engine.extract_text(processed)
    conf_blocks = engine.extract_with_confidence(processed)
    
    elapsed = (time.time() - start_time) * 1000
    return OCRResponse(text=text, confidence_blocks=conf_blocks, processing_time_ms=elapsed)

@app.get("/health")
async def health():
    return {"status": "ok"} 