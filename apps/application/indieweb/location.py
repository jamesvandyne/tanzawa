import json
from typing import Any

from django.contrib.gis.geos import Point
from mf2util import LOCATION_PROPERTIES, string_type


# TODO: Refactor to pass too complex (11)
def get_location(hentry):  # noqa: C901
    # Collect location objects, then follow this algorithm to consolidate their
    # properties:
    # https://indieweb.org/location#How_to_determine_the_location_of_a_microformat
    # Extracted from mf2util
    result: dict[str, Any] = {}
    props = hentry["properties"]
    location_stack = [props]
    for prop in "location", "adr":
        vals = props.get(prop)
        if vals:
            if isinstance(vals[0], string_type):
                location_stack.append({"name": vals})
            else:
                location_stack.append(vals[0].get("properties", {}))

    geo = props.get("geo")
    if geo:
        if isinstance(geo[0], dict):
            location_stack.append(geo[0].get("properties", {}))
        else:
            if geo[0].startswith("geo:"):
                # a geo: URL. try to parse it. https://tools.ietf.org/html/rfc5870
                parts = geo[0][len("geo:") :].split(";")[0].split(",")
                if len(parts) >= 2:
                    location_stack.append(
                        {
                            "latitude": [parts[0]],
                            "longitude": [parts[1]],
                            "altitude": [parts[2]] if len(parts) >= 3 else [],
                        }
                    )

    for prop in LOCATION_PROPERTIES:
        for obj in location_stack:
            if obj and obj.get(prop) and not (obj == props and prop == "name"):
                # normalize to use underscores, rather than - between words
                result.setdefault("location", {})[prop.replace("-", "_")] = obj[prop][0]
    return result


def location_to_pointfield_input(location: Point | dict[str, Any]) -> str:
    if isinstance(location, Point):
        lat = location.y
        lon = location.x
    else:
        lat = float(location["location"]["latitude"])
        lon = float(location["location"]["longitude"])
    # GeoJson coordinates are at longitude / latitude (x,y) order
    # refs: https://geojson.org/geojson-spec.html#id2
    return json.dumps(
        {
            "type": "Point",
            "coordinates": [lon, lat],
        }
    )
