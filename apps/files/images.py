import io
import mimetypes
from pathlib import Path
from typing import Tuple, Union, Optional

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageOps
from django.utils.timezone import now

from .models import TFile


def rotate_image(image_bytes: io.BytesIO, mime_type: str) -> io.BytesIO:
    if not mime_type.startswith("image"):
        return image_bytes

    try:
        image = Image.open(image_bytes)
    except:
        image_bytes.seek(0)
        return image_bytes

    rotated_image = ImageOps.exif_transpose(image)
    rotated_bytes = io.BytesIO()
    rotated_image.save(rotated_bytes, mime_type.split("/")[1])
    rotated_bytes.seek(0)
    return rotated_bytes


def convert_image_format(
    t_file: TFile, target_mime: str, size: Optional[int] = None
) -> Union[Tuple[SimpleUploadedFile, int, int], Tuple[None, None, None]]:
    image = Image.open(t_file.file)
    new_image_data = io.BytesIO()

    ext = mimetypes.guess_extension(target_mime)
    if not ext:
        # unknown mimetype, can't convert
        return None, None, None
    orientation = 274
    try:
        exif = image._getexif()
        if exif:
            exif = dict(exif.items())
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError):
        # There is AttributeError: _getexif sometimes.
        pass

    if size:
        image = image.copy()
        # thumbnail resizes in place. resize returns a new image instance
        image.thumbnail((size, size))
    elif image.width >= 1200 or image.height >= 1200:
        width, height = (image.width // 2, image.height // 2)
        image = image.resize((width, height))
    fmt = ext[1:]

    if fmt == "jpg":
        # .jpg fails but jpeg works ¯\_(ツ)_/¯
        fmt = "jpeg"
    image.save(new_image_data, format=fmt)
    new_image_data.seek(0)
    new_image = Image.open(new_image_data)
    new_filename = t_file.filename.replace(Path(t_file.filename).suffix, ext)
    new_image_data.seek(0)
    upload_file = SimpleUploadedFile(new_filename, new_image_data.read(), target_mime)

    return upload_file, new_image.width, new_image.height


def bytes_as_upload_image(
    image_data: bytes, mime_type: str, filename: Optional[str] = None
) -> Union[Tuple[SimpleUploadedFile, int, int], Tuple[None, None, None]]:
    if not image_data:
        return None, None, None
    ext = mimetypes.guess_extension(mime_type)
    if not ext:
        # unknown mimetype, can't convert
        return None, None, None
    if not filename:
        base_name = now().strftime("%Y-%m-%-dT%H:%M:%S")
        filename = f"{base_name}{ext}"

    upload_file = SimpleUploadedFile(filename, image_data, mime_type)
    if mime_type.startswith("video"):
        return upload_file, 0, 0
    else:
        image = Image.open(io.BytesIO(image_data))
        return upload_file, image.width, image.height
