import pytest
from bs4 import BeautifulSoup
from datetime import datetime
import pytz


@pytest.fixture
def post_xml_soup():
    with open("tests/fixtures/post.xml") as f:
        return BeautifulSoup(f.read(), "xml")


@pytest.fixture
def checkin_xml_soup():
    with open("tests/fixtures/checkin.xml") as f:
        return BeautifulSoup(f.read(), "xml")


class TestExtractEntry:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_entry

        return extract_entry

    def test_extract_post(self, target, post_xml_soup):
        t_entry = target(post_xml_soup)

        assert t_entry.p_name == "The Week #10"
        assert t_entry.p_summary.startswith(
            "It's week #10 - I've managed to make it to double digit weekly updates!"
        )
        assert t_entry.e_content.startswith("<ul>")


class TestExtractCategories:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_categories

        return extract_categories

    def test_extract_categories(self, target, post_xml_soup):
        categories = target(post_xml_soup)
        assert categories == [("The Week", "the-week")]


class TestExtractPostKind:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_post_kind

        return extract_post_kind

    def test_extract_post_kind(self, target, post_xml_soup):
        categories = target(post_xml_soup)
        assert categories == [("Article", "article")]


class TestExtractPostFormat:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_post_format

        return extract_post_format

    def test_extract_post_kind(self, target, checkin_xml_soup):
        categories = target(checkin_xml_soup)
        assert categories == [("Status", "post-format-status")]


class TestExtractPublishedDate:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_published_date

        return extract_published_date

    def test_extract_published_date(self, target, post_xml_soup):
        assert datetime(
            year=2020, month=9, day=14, hour=20, minute=30, second=23, tzinfo=pytz.utc
        ) == target(post_xml_soup)


class TestExtractPhoto:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_photo

        return extract_photo

    def test_extract_photo(self, target, checkin_xml_soup):
        photos = target(checkin_xml_soup)
        assert photos == [
            "https://fastly.4sqi.net/img/general/original/89277993_FzCrX1lGY8katwtWXKivLtYCtjI1sA9pb_bXODpP1Bc.jpg"
        ]
