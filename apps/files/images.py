from django.core.files.uploadedfile import SimpleUploadedFile
from typing import Optional, Tuple, Union
import mimetypes
import io
from PIL import Image

from .models import TFile


def convert_image_format(t_file: TFile, to_mime: str) -> Union[Tuple[SimpleUploadedFile, int, int], Tuple[None, None, None]]:
    image = Image.open(t_file.file)
    new_image_data = io.BytesIO()
    try:
        ext = mimetypes.guess_extension(to_mime)[1:]
    except TypeError:
        # unknown mimetype, can't convert
        return None, None, None
    image.save(new_image_data, format=ext)
    new_image_data.seek(0)
    new_image = Image.open(new_image_data)

    # generate filename based on ext

    upload_file = SimpleUploadedFile(t_file.filename, new_image, to_mime)
    return upload_file, new_image.width, new_image.height
