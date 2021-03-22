import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from wordpress.models import TCategory


@pytest.mark.django_db
class TestWordpressUploadFrom:
    @pytest.fixture
    def target(self):
        from wordpress.forms import WordpressUploadForm

        return WordpressUploadForm

    @pytest.fixture
    def export_file(self):
        with open("tests/fixtures/wp.xml", "rb") as wp:
            return SimpleUploadedFile(
                "wp.xml",
                wp.read(),
                "text/xml",
            )

    @pytest.fixture
    def form_data(self, export_file):
        return {"export_file": export_file}

    def test_valid(self, target, form_data):

        form = target(files=form_data)
        assert form.is_valid()

        instance = form.save()

        assert instance.link == "https://jamesvandyne.com"
        assert instance.base_site_url == "https://jamesvandyne.com"
        assert instance.base_blog_url == "https://jamesvandyne.com"

        assert TCategory.objects.count() == 11
