from pydantic import BaseModel
from typing import List, Tuple, Optional

class OCRResponse(BaseModel):
    text: str
    confidence_blocks: Optional[List[Tuple[str, float]]] = None
    processing_time_ms: float 