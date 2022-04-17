import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.wordpress.models import TWordpress

MAIN_DIRECTORY = Path("wordpress/")


def _md5_sum_for_file(file_field) -> str:
    hash_md5 = hashlib.md5()
    for chunk in file_field.chunks(4096):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


def wordpress_upload_to(instance: "TWordpress", filename: str) -> Path:
    instance.filename = filename
    file_directory = MAIN_DIRECTORY / "import"
    file_name = _md5_sum_for_file(instance.export_file)
    return file_directory / file_name
