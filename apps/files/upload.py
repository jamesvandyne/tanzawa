import hashlib
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from django.utils.timezone import now

if TYPE_CHECKING:
    from .models import TFile, TResizedImage, TFormatImage

MAIN_DIRECTORY = Path("uploads/")
DATE_DIRECTORY = "%Y/%m/%d"


def _md5_sum_for_file(file_field) -> str:
    hash_md5 = hashlib.md5()
    for chunk in file_field.chunks(4096):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_to(instance: "TFile", filename: str) -> Path:
    instance.filename = filename
    file_directory = MAIN_DIRECTORY / now().strftime(DATE_DIRECTORY) / str(instance.uuid)
    file_name = _md5_sum_for_file(instance.file)
    return file_directory / file_name


def format_upload_to(instance: "TFormatImage", filename: str) -> Path:
    file_directory = Path(instance.t_file.file.name).parent
    file_name = _md5_sum_for_file(instance.file)
    return file_directory / file_name


def resized_upload_to(instance: "TResizedImage", filename: str) -> Path:
    file_directory = Path(instance.t_file.file.name).parent
    file_name = _md5_sum_for_file(instance.file)
    return file_directory / file_name
