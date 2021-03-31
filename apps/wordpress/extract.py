from typing import Dict, Any, ByteString
from bs4 import BeautifulSoup
import phpserialize

from .models import TWordpressAttachment


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
