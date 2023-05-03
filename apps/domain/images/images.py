import io
import mimetypes
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import now
from PIL import Image, ImageOps

from data.files import models as file_models


def rotate_image(image_bytes: io.BytesIO, mime_type: str) -> io.BytesIO:
    if not mime_type.startswith("image"):
        return image_bytes

    try:
        image = Image.open(image_bytes)
    except Exception:
        image_bytes.seek(0)
        return image_bytes

    rotated_image = ImageOps.exif_transpose(image)
    rotated_bytes = io.BytesIO()
    rotated_image.save(rotated_bytes, mime_type.split("/")[1])
    rotated_bytes.seek(0)
    return rotated_bytes


def convert_image_format(
    t_file: file_models.TFile, target_mime: str, longest_edge: int | None = None
) -> tuple[SimpleUploadedFile, int, int] | tuple[None, None, None]:
    image = Image.open(t_file.file)
    file_extension = mimetypes.guess_extension(target_mime)
    if not file_extension:
        # unknown mimetype, can't convert
        return None, None, None

    image = _get_rotated_image(image)

    if longest_edge:
        image = _get_thumbnail(image, longest_edge)
    elif image.width >= 1200 or image.height >= 1200:
        width, height = (image.width // 2, image.height // 2)
        image = image.resize((width, height))

    new_format_data = _change_image_format(image, format=file_extension[1:])

    new_image = Image.open(new_format_data)
    new_filename = t_file.filename.replace(Path(t_file.filename).suffix, file_extension)
    new_format_data.seek(0)

    upload_file = SimpleUploadedFile(new_filename, new_format_data.read(), target_mime)

    return upload_file, new_image.width, new_image.height


def _get_thumbnail(image: Image, longest_edge: int) -> Image:
    image = image.copy()
    # thumbnail resizes in place. resize returns a new image instance
    image.thumbnail((longest_edge, longest_edge))
    return image


def _change_image_format(image: Image, format: str) -> io.BytesIO:
    new_image_data = io.BytesIO()

    if format == "jpg":
        # .jpg fails but jpeg works ¯\_(ツ)_/¯
        format = "jpeg"
    image.save(new_image_data, format=format)
    new_image_data.seek(0)
    return new_image_data


def _get_rotated_image(image: Image) -> Image:
    orientation = 274
    try:
        exif = image._getexif()
    except (AttributeError, KeyError):
        # There is AttributeError: _getexif sometimes.
        pass
    else:
        exif = dict(exif.items())
        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
    return image


def bytes_as_upload_image(
    image_data: bytes, mime_type: str, filename: str | None = None
) -> tuple[SimpleUploadedFile, int, int] | tuple[None, None, None]:
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
