from typing import Optional
from io import BytesIO
from exif import Image
from django.contrib.gis.geos import Point


def remove_gps_exif(image) -> Optional[BytesIO]:
    with Image(image) as img:
        if not img.has_exif:
            return None
        for key in dir(img):
            if "gps" in key:
                img.delete(key)
        new_file = BytesIO()
        new_file.write(img.get_file())
        new_file.seek(0)
        return new_file


def dms_to_dd(degree, minute, second) -> float:
    """ Convert from degree, minutes, seconds to a decimal degree for storage in a Point"""
    sign = -1 if degree < 0 else 1
    return sign * (int(degree) + float(minute) / 60 + float(second) / 3600)


def get_location(image) -> Optional[Point]:
    img = Image(image)
    if not img.has_exif:
        return None
    gps_latitude = img.get('gps_latitude')
    gps_longitude = img.get('gps_longitude')
    if gps_latitude and gps_longitude:
        return Point(dms_to_dd(*gps_longitude), dms_to_dd(*gps_latitude))
    return None
