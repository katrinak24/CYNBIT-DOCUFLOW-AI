from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}

def validate_upload(filename: str, size_bytes: int, max_mb: int = 15) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}. Upload PDF or an image.")
    if size_bytes > max_mb * 1024 * 1024:
        raise ValueError(f"File exceeds the {max_mb} MB upload limit.")
