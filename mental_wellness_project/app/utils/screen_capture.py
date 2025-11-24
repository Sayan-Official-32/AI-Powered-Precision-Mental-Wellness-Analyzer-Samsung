import base64
import io
from typing import Optional

from PIL import Image


def decode_base64_screen(image_b64: str) -> Optional[Image.Image]:
    if not image_b64:
        return None

    if "," in image_b64:
        image_b64 = image_b64.split(",")[1]

    try:
        return Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")
    except Exception:
        return None
