from datetime import datetime
from typing import Dict, Any, ByteString, List, Tuple, Union, Optional
from bs4 import BeautifulSoup
import phpserialize
from django.utils.timezone import make_aware
import pytz
from django.contrib.gis.geos import Point
from .models import TWordpressAttachment
from indieweb.extract import LinkedPage, LinkedPageAuthor
from post.models import TPost, MPostKind, MPostStatus, MPostStatuses

from entry.models import TEntry, TSyndication, TBookmark, TLocation, TCheckin, TReply


def extract_attachment_meta(attachment: TWordpressAttachment) -> Dict[ByteString, Any]:
    soup = BeautifulSoup(attachment.t_wordpress.export_file.read(), "xml")
    guid = soup.find("guid", text=attachment.guid)
    item = guid.parent
    attachment_meta_key = item.find("wp:meta_key", text="_wp_attachment_metadata")
    attachment_meta_data = attachment_meta_key.find_next("wp:meta_value").text

    phpserialize.loads(attachment_meta_key.encode("utf8"))

    categories = set(soup.find_all("category", attrs={"domain": "category"}))
    return [
        TCategory(name=category.text, nice_name=category.attrs["nicename"])
        for category in categories
    ]


def extract_post_status(soup: BeautifulSoup) -> str:
    status_map = {"publish": MPostStatuses.published, "draft": MPostStatuses.draft}
    return status_map.get(soup.find("status").text, MPostStatuses.draft)


def extract_published_date(soup: BeautifulSoup) -> datetime:
    pub_date = datetime.strptime(soup.find("post_date_gmt").text, "%Y-%m-%d %H:%M:%S")
    return make_aware(pub_date, pytz.utc)


def extract_entry(soup: BeautifulSoup) -> TEntry:
    p_summary = BeautifulSoup(
        soup.find("description").text or soup.find("encoded").text[:255], "html5lib"
    )
    return TEntry(
        p_name=soup.find("title").text,
        p_summary=p_summary.text.strip(),
        e_content=soup.find("encoded").text,
    )


def extract_categories(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    # Returns a tuple ("name", "nice-name")
    return [
        (cat.text, cat.attrs["nicename"])
        for cat in set(soup.find_all("category", attrs={"domain": "category"}))
    ]


def extract_post_kind(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    # Returns a tuple ("name", "nice-name")
    return [
        (cat.text, cat.attrs["nicename"])
        for cat in set(soup.find_all("category", attrs={"domain": "kind"}))
    ]


def extract_post_format(soup: BeautifulSoup) -> List[Tuple[str, str]]:
    # Returns a tuple ("name", "nice-name")
    return [
        (cat.text, cat.attrs["nicename"])
        for cat in set(soup.find_all("category", attrs={"domain": "post_format"}))
    ]


def _extract_meta_list(soup: BeautifulSoup, key:str) -> List[str]:
    values = []
    for item in soup.find("meta_key", text=key):
        value = item.find_next("meta_value")
        value_dict: Dict[int, bytes] = phpserialize.loads(value.text.encode("utf8"))
        values.extend([url.decode("utf8") for url in value_dict.values()])
    return values


def extract_photo(soup: BeautifulSoup) -> List[str]:
    return _extract_meta_list(soup, "mf2_photo")


def extract_syndication(soup: BeautifulSoup) -> List[str]:
    return _extract_meta_list(soup, "mf2_syndication")


def _get_item_as_string(value_dict: Dict[bytes, Dict[int, bytes]], key: bytes) -> bytes:
    value = value_dict.get(key)
    if value:
        try:
            return value[0]
        except KeyError:
            pass
    return b''


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
        properties = value_dict.get(b'properties', {})
        return {
            "street_address": _get_item_as_string(properties, b"street-address").decode("utf8"),
            "locality": _get_item_as_string(properties, b"locality").decode("utf8"),
            "region": _get_item_as_string(properties, b"region").decode("utf8"),
            "country_name": _get_item_as_string(properties, b"country-name").decode("utf8"),
            "postal_code": _get_item_as_string(properties, b"postal-code").decode("utf8"),
            "point": Point(_get_item_as_string(properties, b"latitude"),
                           _get_item_as_string(properties, b"longitude")),
        }
    return {}


def extract_checkin(soup: BeautifulSoup) -> Dict[str, Union[str, Point]]:
    location_key = soup.find("meta_key", text="mf2_checkin")
    if location_key:
        value = location_key.find_next("meta_value")
        value_dict = phpserialize.loads(value.text.encode("utf8"))
        properties = value_dict.get(b'properties', {})
        return {
            "name": _get_item_as_string(properties, b"name").decode("utf8"),
            "url": _get_item_as_string(properties, b"url").decode("utf8"),
        }
    return {}


def _extract_author(author: Dict[bytes, Dict[int, bytes]]) -> Optional[LinkedPageAuthor]:
    properties = author.get(b"properties")
    if properties:
        return LinkedPageAuthor(
            name=_get_item_as_string(properties, b"name").decode("utf8"),
            url=_get_item_as_string(properties, b"url").decode("utf8"),
            photo=_get_item_as_string(properties, b"photo").decode("utf8")
        )
    return None


def extract_in_reply_to(soup: BeautifulSoup) -> Optional[LinkedPage]:
    reply_to = soup.find("meta_key", text="mf2_in-reply-to")
    if reply_to:
        value = reply_to.find_next("meta_value")
        value_dict = phpserialize.loads(value.text.encode("utf8"))
        properties = value_dict.get(b'properties', {})
        import pdb; pdb.set_trace()
        return LinkedPage(
            url=_get_item_as_string(properties, b"url").decode("utf8"),
            title=_get_item_as_string(properties, b"name").decode("utf8"),
            description=_get_item_as_string(properties, b"summary").decode("utf8"),
            author=_extract_author(properties.get(b"author", {}))
        )
    return None