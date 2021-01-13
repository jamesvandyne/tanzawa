import io
import mimetypes
from pathlib import Path
from typing import Tuple, Union

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from .models import TFile


def convert_image_format(
    t_file: TFile, target_mime: str
) -> Union[Tuple[SimpleUploadedFile, int, int], Tuple[None, None, None]]:
    image = Image.open(t_file.file)
    new_image_data = io.BytesIO()

    ext = mimetypes.guess_extension(target_mime)
    if not ext:
        # unknown mimetype, can't convert
        return None, None, None
    image.save(new_image_data, format=ext[1:])
    new_image_data.seek(0)
    new_image = Image.open(new_image_data)

    new_filename = t_file.filename.replace(Path(t_file.filename).suffix, ext)
    new_image_data.seek(0)
    upload_file = SimpleUploadedFile(new_filename, new_image_data.read(), target_mime)

    return upload_file, new_image.width, new_image.height
