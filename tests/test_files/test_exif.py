import io
import pytest
from exif import Image


class TestScrubExif:
    @pytest.fixture
    def target(self):
        from files.exif import scrub_exif

        return scrub_exif

    @pytest.fixture
    def image(self):
        with open("tests/fixtures/img_gps.jpeg", "rb") as f:
            return io.BytesIO(f.read())

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
