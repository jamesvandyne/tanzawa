import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

from django.utils.timezone import now

if TYPE_CHECKING:
    from .models import TWordpress

MAIN_DIRECTORY = Path("wordpress/")


def _md5_sum_for_file(file_field) -> str:
    hash_md5 = hashlib.md5()
    for chunk in file_field.chunks(4096):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


def wordpress_upload_to(instance: "TWordpress", filename: str) -> Path:
    instance.filename = filename
    file_directory = MAIN_DIRECTORY / "import" / str(instance.uuid)
    file_name = _md5_sum_for_file(instance.file)
    return file_directory / file_name
