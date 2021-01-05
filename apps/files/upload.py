from typing import TYPE_CHECKING
from pathlib import Path
import hashlib
import uuid

if TYPE_CHECKING:
    from .models import TFile

DIRECTORY = Path("uploads/%Y/%m/%d/")


def upload_to(instance: "TFile", filename: str) -> Path:
    file_directory = str(uuid.uuid4())
    hash_md5 = hashlib.md5()
    with instance.file.open() as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    file_name = hash_md5.hexdigest()
    return DIRECTORY / file_directory / file_name
