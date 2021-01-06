from django.utils.timezone import now
from typing import TYPE_CHECKING
from pathlib import Path
import hashlib
import uuid

if TYPE_CHECKING:
    from .models import TFile

MAIN_DIRECTORY = Path("uploads/")
DATE_DIRECTORY = "%Y/%m/%d"


def upload_to(instance: "TFile", filename: str) -> Path:
    file_directory = MAIN_DIRECTORY / now().strftime(DATE_DIRECTORY) / str(uuid.uuid4())
    hash_md5 = hashlib.md5()
    for chunk in instance.file.chunks(4096):
        hash_md5.update(chunk)
    file_name = hash_md5.hexdigest()
    return file_directory / file_name
