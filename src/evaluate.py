import Levenshtein

def cer(ground_truth: str, predicted: str) -> float:
    """Character Error Rate (0.0 to 1.0)."""
    if len(ground_truth) == 0:
        return 1.0 if len(predicted) > 0 else 0.0
    return Levenshtein.distance(ground_truth, predicted) / len(ground_truth)

def wer(ground_truth: str, predicted: str) -> float:
    """Word Error Rate."""
    gt_words = ground_truth.split()
    pred_words = predicted.split()
    return Levenshtein.distance(" ".join(gt_words), " ".join(pred_words)) / max(len(gt_words), 1) 