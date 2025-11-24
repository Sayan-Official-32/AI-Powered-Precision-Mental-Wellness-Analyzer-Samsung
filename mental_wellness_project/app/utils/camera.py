import base64
import io
from typing import Optional

import cv2
import numpy as np
from PIL import Image


def decode_base64_image(image_b64: str) -> Optional[np.ndarray]:
    """
    Accepts a browser `canvas.toDataURL` string (data:image/png;base64,....)
    and returns an OpenCV BGR matrix. Returns None if decoding fails.
    """

    if not image_b64:
        return None

    try:
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception:
        return None
