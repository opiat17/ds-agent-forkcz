from pathlib import Path
from typing import List


def get_media_files() -> List[str]:
    media_dir = Path("media")
    if not media_dir.exists():
        return []

    supported_formats = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4', '.webm']

    media_files = []
    for file in media_dir.iterdir():
        if file.is_file() and file.suffix.lower() in supported_formats:
            media_files.append(str(file))

    return media_files