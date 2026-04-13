import os
import yaml
from pathlib import Path
from PIL import Image
import mlflow

from src.ocr_engine import OCREngine
from src.preprocessing import preprocess_image
from src.evaluate import cer
from src.mlflow_logger import setup_mlflow, log_ocr_run

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def run_experiment(preprocessing_method: str = "none"):
    setup_mlflow()
    engine = OCREngine()
    
    raw_dir = Path(config["data"]["raw_dir"])
    gt_dir = Path(config["data"]["ground_truth_dir"])
    
    errors = []
    total_chars = 0
    for img_path in raw_dir.glob("*.*"):
        if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
            continue
        gt_path = gt_dir / f"{img_path.stem}.txt"
        if not gt_path.exists():
            print(f"Warning: No ground truth for {img_path.name}, skipping.")
            continue
        
        # Load and preprocess image
        image = Image.open(img_path)
        processed = preprocess_image(image, preprocessing_method)
        
        # OCR
        pred_text = engine.extract_text(processed)
        gt_text = gt_path.read_text(encoding="utf-8").strip()
        
        # Calculate CER
        error = cer(gt_text, pred_text)
        errors.append(error)
        total_chars += len(gt_text)
    
    if not errors:
        print("No valid images with ground truth found.")
        return
    
    mean_cer = sum(errors) / len(errors)
    print(f"Preprocessing: {preprocessing_method} | Mean CER: {mean_cer:.4f}")
    
    # Log to MLflow
    params = {
        "preprocessing": preprocessing_method,
        "languages": config["ocr"]["languages"],
        "num_samples": len(errors)
    }
    metrics = {"mean_cer": mean_cer, "total_chars": total_chars}
    log_ocr_run(params, metrics)
    
    # Also log config file as artifact
    mlflow.log_artifact("config.yaml")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--preprocess", default="none", choices=["none", "grayscale", "threshold", "denoise"])
    args = parser.parse_args()
    run_experiment(args.preprocess) 