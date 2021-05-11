from io import BytesIO
from typing import Any, Dict, Optional, Tuple

from django.contrib.gis.geos import Point
from exif import Image


def extract_exif(image) -> Dict[str, Any]:
    img = Image(image)
    exif = {}
    if not img.has_exif:
        return exif

    for key in dir(img):
        value = img.get(key)
        if not value:
            continue
        if hasattr(value, "asdict"):
            value = value.asdict()
        exif[key] = value
    return exif


def scrub_exif(image: BytesIO) -> Optional[BytesIO]:
    img = Image(image)
    if not img.has_exif:
        return None
    img.delete_all()
    new_file = BytesIO()
    new_file.write(img.get_file())
    new_file.seek(0)
    return new_file


def dms_to_dd(degree, minute, second) -> float:
    """Convert from degree, minutes, seconds to a decimal degree for storage in a Point"""
    sign = -1 if degree < 0 else 1
    return sign * (int(degree) + float(minute) / 60 + float(second) / 3600)


def get_location(exif_dict: Dict[str, Tuple[float, float, float]]) -> Optional[Point]:
    """Convert the gps degree/minute/second to a Point"""
    gps_latitude = exif_dict.get("gps_latitude")
    gps_longitude = exif_dict.get("gps_longitude")
    if gps_latitude and gps_longitude:
        return Point(dms_to_dd(*gps_longitude), dms_to_dd(*gps_latitude))
    return None
