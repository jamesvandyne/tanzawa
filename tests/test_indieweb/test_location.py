import json

import pytest
from django.contrib.gis.geos import Point


class TestLocationToPointField:
    @pytest.fixture
    def target(self):
        from indieweb.location import location_to_pointfield_input

        return location_to_pointfield_input

    @pytest.mark.parametrize(
        "location",
        [
            {
                "location": {
                    "latitude": "50.1",
                    "longitude": "-100.2",
                }
            },
            Point(x=-100.2, y=50.1),
        ],
    )
    def test_converts_to_geojson(self, target, location):
        ret = target(location)
        assert ret == json.dumps({"type": "Point", "coordinates": [-100.2, 50.1]})
