from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError


SUPPORTED_UPLOAD_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_UPLOAD_BYTES = 12 * 1024 * 1024


def validate_uploaded_image(uploaded_file):
    content_type = getattr(uploaded_file, "content_type", "") or ""
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        return "照片太大了，目前先支援 12MB 以下的圖片。可以先截圖或壓縮後再傳一次。"
    if content_type not in SUPPORTED_UPLOAD_TYPES:
        return "這個照片格式目前還不穩定。請先改傳 JPG、PNG 或 WebP，我就可以幫你看。"
    return ""


def prepare_image_data_url(image_path: str, max_side: int = 1600, quality: int = 84) -> str:
    path = Path(image_path)
    try:
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image)
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            elif image.mode == "L":
                image = image.convert("RGB")
            image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=quality, optimize=True)
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("無法讀取這張照片，請改傳 JPG、PNG 或 WebP。") from exc

    import base64

    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"
