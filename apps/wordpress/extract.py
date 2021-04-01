from typing import Dict, Any, ByteString, List, Tuple
from bs4 import BeautifulSoup
import phpserialize

from .models import TWordpressAttachment
from post.models import TPost

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
