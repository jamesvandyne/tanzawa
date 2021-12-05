from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import phpserialize
import pytz
from bs4 import BeautifulSoup
from django.contrib.gis.geos import Point
from django.utils.timezone import make_aware
from entry.models import TEntry
from indieweb.extract import LinkedPage, LinkedPageAuthor
from post.models import MPostStatuses


def extract_internal_links(soup: BeautifulSoup, domain) -> List[BeautifulSoup]:
    return [link for link in soup.find_all("a") if domain in link["href"]]


def extract_images(soup: BeautifulSoup, domain) -> List[BeautifulSoup]:
    return [img for img in soup.find_all("img") if domain in img["src"]]


def extract_post_status(soup: BeautifulSoup) -> str:
    status_map = {"publish": MPostStatuses.published, "draft": MPostStatuses.draft}
    return status_map.get(soup.find("status").text, MPostStatuses.draft)


def extract_published_date(soup: BeautifulSoup) -> Optional[datetime]:
    try:
        pub_date = datetime.strptime(soup.find("post_date_gmt").text, "%Y-%m-%d %H:%M:%S")
        return make_aware(pub_date, pytz.utc)
    except ValueError:
        # draft posts
        return None


def extract_entry(soup: BeautifulSoup) -> TEntry:
    p_summary = BeautifulSoup(soup.find("description").text or soup.find("encoded").text[:255], "html5lib")
    return TEntry(
        p_name=soup.find("title").text,
        p_summary=p_summary.text.strip(),
        e_content=soup.find("encoded").text,
    )


def extract_categories(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    # Returns a tuple ("name", "nice-name")
    return [(cat.text, cat.attrs["nicename"]) for cat in set(soup.find_all("category", attrs={"domain": "category"}))]


def extract_post_kind(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    # Returns a tuple ("name", "nice-name")
    return [(cat.text, cat.attrs["nicename"]) for cat in set(soup.find_all("category", attrs={"domain": "kind"}))]


def extract_post_format(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    # Returns a tuple ("name", "nice-name")
    return [
        (cat.text, cat.attrs["nicename"]) for cat in set(soup.find_all("category", attrs={"domain": "post_format"}))
    ]


def _extract_meta_list(soup: BeautifulSoup, key: str) -> List[str]:
    values = []
    for item in soup.find("meta_key", text=key) or []:
        value = item.find_next("meta_value")
        value_dict: Dict[int, bytes] = phpserialize.loads(value.text.encode("utf8"))
        values.extend([url.decode("utf8") for url in value_dict.values()])
    return values


def extract_photo(soup: BeautifulSoup) -> List[str]:
    return _extract_meta_list(soup, "mf2_photo")


def extract_syndication(soup: BeautifulSoup) -> List[str]:
    return _extract_meta_list(soup, "mf2_syndication")


def _get_first_value_for_key(value_dict: Dict[bytes, Dict[int, bytes]], key: bytes) -> Union[bytes, float]:
    """
    php arrays get decoded as python dictionaries where the array's index becomes the key in the python dict
    e.g.
    b'street-address': {0: b'\xe9\x83\xbd\xe7\xad\x91\xe5\x8c\xba\xe6\x8a\x98\xe6\x9c\xac\xe7\x94\xba201-1'}

    Extract the value for the key 0
    """
    value = value_dict.get(key)
    if value:
        if isinstance(value, bytes):
            return value
        try:
            return value[0]
        except KeyError:
            return b""
    return b""


def get_string_from_dict(value_dict: Dict[bytes, Dict[int, bytes]], key: bytes) -> str:
    value = _get_first_value_for_key(value_dict=value_dict, key=key)
    if isinstance(value, bytes):
        return value.decode("utf8")
    return str(value)


def extract_location(soup: BeautifulSoup) -> Dict[str, Union[str, Point]]:
    location_key = soup.find("meta_key", text="mf2_location")
    if location_key:
        """
        {b'type':
            {0: b'h-adr'},
        b'properties': {
            b'latitude': {0: 35.522764},
            b'longitude': {0: 139.590671},
            b'street-address': {0: b'\xe9\x83\xbd\xe7\xad\x91\xe5\x8c\xba\xe6\x8a\x98\xe6\x9c\xac\xe7\x94\xba201-1'},
            b'locality': {0: b'Yokohama'},
            b'region': {0: b'Kanagawa'},
            b'country-name': {0: b'Japan'},
            b'postal-code': {0: b'224-0043'}
            }
        }
        """
        value = location_key.find_next("meta_value")
        value_dict = phpserialize.loads(value.text.encode("utf8"))
        properties = value_dict.get(b"properties", {})
        return {
            "street_address": get_string_from_dict(properties, b"street-address"),
            "locality": get_string_from_dict(properties, b"locality"),
            "region": get_string_from_dict(properties, b"region"),
            "country_name": get_string_from_dict(properties, b"country-name"),
            "postal_code": get_string_from_dict(properties, b"postal-code"),
            "point": Point(
                _get_first_value_for_key(properties, b"latitude"),
                _get_first_value_for_key(properties, b"longitude"),
            ),
        }
    return {}


def extract_checkin(soup: BeautifulSoup) -> Dict[str, Union[str, Point]]:
    location_key = soup.find("meta_key", text="mf2_checkin")
    if location_key:
        value = location_key.find_next("meta_value")
        value_dict = phpserialize.loads(value.text.encode("utf8"))
        properties = value_dict.get(b"properties", {})
        return {
            "name": get_string_from_dict(properties, b"name"),
            "url": get_string_from_dict(properties, b"url"),
        }
    return {}


def _extract_author(author: Dict[bytes, Dict[bytes, Dict[int, bytes]]]) -> Optional[LinkedPageAuthor]:
    properties = author.get(b"properties")
    if properties:
        return LinkedPageAuthor(
            name=get_string_from_dict(properties, b"name"),
            url=get_string_from_dict(properties, b"url"),
            photo=get_string_from_dict(properties, b"photo"),
        )
    return None


def _extract_cite(soup: BeautifulSoup, key: str) -> Optional[LinkedPage]:
    cite = None
    cites = soup.find_all("meta_key", text=key)
    for c in cites:
        if c.parent.name == "commentmeta":
            continue
        cite = c
    if cite:
        value = cite.find_next("meta_value")
        value_dict = phpserialize.loads(value.text.encode("utf8"))
        properties = value_dict.get(b"properties", {})
        return LinkedPage(
            url=get_string_from_dict(properties, b"url"),
            title=get_string_from_dict(properties, b"name"),
            description=get_string_from_dict(properties, b"summary"),
            author=_extract_author(properties.get(b"author", {})),
        )
    return None


def extract_in_reply_to(soup: BeautifulSoup) -> Optional[LinkedPage]:
    return _extract_cite(soup, "mf2_in-reply-to")


def extract_bookmark(soup: BeautifulSoup) -> Optional[LinkedPage]:
    return _extract_cite(soup, "mf2_bookmark-of")
