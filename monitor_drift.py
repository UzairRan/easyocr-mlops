import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from pathlib import Path
import cv2
from PIL import Image
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def compute_image_features(image_path):
    img = cv2.imread(str(image_path))
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = gray.mean()
    return {"sharpness": laplacian_var, "brightness": brightness}

def generate_drift_report(reference_dir, current_dir):
    ref_features = []
    for f in Path(reference_dir).glob("*.*"):
        feat = compute_image_features(f)
        if feat:
            feat["image"] = f.name
            ref_features.append(feat)
    
    cur_features = []
    for f in Path(current_dir).glob("*.*"):
        feat = compute_image_features(f)
        if feat:
            feat["image"] = f.name
            cur_features.append(feat)
    
    ref_df = pd.DataFrame(ref_features)
    cur_df = pd.DataFrame(cur_features)
    
    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref_df, current_data=cur_df)
    report.save_html("drift_report.html")

if __name__ == "__main__":
    generate_drift_report("data/raw", "data/new_images")  # adjust paths 