import io

import pytest
from exif import Image


@pytest.fixture
def image():
    with open("tests/fixtures/img_gps.jpeg", "rb") as f:
        return io.BytesIO(f.read())


class TestScrubExif:
    @pytest.fixture
    def target(self):
        from files.exif import scrub_exif

        return scrub_exif

    def test_removes_location(self, target, image):
        """
        scrub_exif removes all exif data, except DateTime.

        We mostly want to confirm that we're removing the location from uploaded images.
        """
        orig = Image(image.read())
        image.seek(0)
        assert orig.get("gps_latitude")
        assert orig.get("gps_longitude")
        scrubbed_bytes = target(image)
        scrubbed_image = Image(scrubbed_bytes)
        assert scrubbed_image.get("gps_latitude") is None
        assert scrubbed_image.get("gps_longitude") is None


class TestExtractsLocation:
    @pytest.fixture
    def target(self):
        from files.exif import get_location

        return get_location

    @pytest.fixture
    def exif_dict(self, image):
        img_dict = Image(image.read())
        return img_dict

    def test_extracts_point(self, target, exif_dict):
        result = target(exif_dict)
        assert result.x == 139.4856722222222  # lon
        assert result.y == 35.31948333333334  # lat
