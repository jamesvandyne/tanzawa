"""
Mercator calculations used to fix the projection from geo-coordinate to x,y (flat) coordinates.
Adapted from: https://wiki.openstreetmap.org/wiki/Mercator
"""

import math

EARTH_RADIUS_KM = 6378137.0


def y2lat(y):
    return math.degrees(2 * math.atan(math.exp(y / EARTH_RADIUS_KM)) - math.pi / 2.0)


def lat2y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * EARTH_RADIUS_KM


def x2lng(x):
    return math.degrees(x / EARTH_RADIUS_KM)


def lon2x(lon):
    return math.radians(lon) * EARTH_RADIUS_KM
