from datetime import datetime
from typing import Dict, Any, ByteString, List, Tuple
from bs4 import BeautifulSoup
import phpserialize
from django.utils.timezone import make_aware
import pytz

from .models import TWordpressAttachment
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
