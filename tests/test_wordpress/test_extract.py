from datetime import datetime

import pytest
from bs4 import BeautifulSoup
from django.contrib.gis.geos import Point
import pytz

from indieweb.extract import LinkedPageAuthor, LinkedPage


@pytest.fixture
def post_xml_soup():
    with open("tests/fixtures/post.xml") as f:
        return BeautifulSoup(f.read(), "xml")


@pytest.fixture
def checkin_xml_soup():
    with open("tests/fixtures/checkin.xml") as f:
        return BeautifulSoup(f.read(), "xml")


@pytest.fixture
def reply_xml_soup():
    with open("tests/fixtures/replyto.xml") as f:
        return BeautifulSoup(f.read(), "xml")


@pytest.fixture
def bookmark_xml_soup():
    with open("tests/fixtures/bookmark.xml") as f:
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


class TestExtractSyndication:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_syndication

        return extract_syndication

    def test_extract_syndication(self, target, checkin_xml_soup):
        urls = target(checkin_xml_soup)
        assert urls == [
            "https://www.swarmapp.com/user/89277993/checkin/5f6563d6a183c074f5e2e472"
        ]


class TestExtractLocation:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_location

        return extract_location

    def test_extract_location(self, target, checkin_xml_soup):
        location = target(checkin_xml_soup)
        assert location == {
            "street_address": "都筑区折本町201-1",
            "locality": "Yokohama",
            "region": "Kanagawa",
            "country_name": "Japan",
            "postal_code": "224-0043",
            "point": Point(35.522764,  139.590671),
        }


class TestExtractCheckin:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_checkin

        return extract_checkin

    def test_extract_checkin(self, target, checkin_xml_soup):
        checkin = target(checkin_xml_soup)
        assert checkin == {
            "name": "IKEA Restaurant & Cafe (IKEAレストラン&カフェ)",
            "url": "https://foursquare.com/v/4e745d4f1838f918895cf6fd"
        }


class TestExtractReply:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_in_reply_to

        return extract_in_reply_to

    def test_extract_reply(self, target, reply_xml_soup):
        reply = target(reply_xml_soup)
        assert reply == LinkedPage(
            url="https://jamesg.blog/2020/10/19/a-conflict-with-rss",
            title="A Conflict with RSS",
            description="On my vacation, I took some time away from technology.",
            author=LinkedPageAuthor(
                name="capjamesg",
                url="https://jamesg.blog",
                photo="https://jamesg.blog/assets/coffeeshop.jpg"
            )
        )


class TestExtractBookmark:
    @pytest.fixture
    def target(self):
        from wordpress.extract import extract_bookmark

        return extract_bookmark

    def test_extract_reply(self, target, bookmark_xml_soup):
        bookmark = target(bookmark_xml_soup)
        assert bookmark == LinkedPage(
            url="https://www.nikkei.com/article/DGXMZO65278360R21C20A0MM8000/",
            title="温暖化ガス排出、2050年に実質ゼロ　菅首相が表明へ　　:日本経済新聞",
            description="■26日、就任後初の所信演説で方針を示す■ＥＵが既に掲げた目標を日本もようやく追いかける■高い基準の達成に日本企業も厳しい対応を迫られる",
            author=None
        )
