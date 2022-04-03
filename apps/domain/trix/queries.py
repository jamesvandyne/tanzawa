import json
from typing import Dict, List

from bs4 import BeautifulSoup


def extract_attachments(html: str) -> List[Dict[str, str]]:
    """
    Extract trix attachment json dict from html

    {
        'contentType': 'image/png',
        'filename': 'tanzawa.png',
        'filesize': 30508,
        'height': 518,
        'href': 'http://127.0.0.1:8000/files/543e4f8e-464d-46ec-998b-d2e3e6b07243?content-disposition=attachment',
        'url': 'http://127.0.0.1:8000/files/543e4f8e-464d-46ec-998b-d2e3e6b07243',
        'width': 1880
    }

    """
    attachments = []
    soup = BeautifulSoup(html, "html.parser")
    for attachment in soup.select("figure[data-trix-attachment]"):
        data = json.loads(attachment["data-trix-attachment"])
        attachments.append(data)
    return attachments


def extract_attachment_urls(html: str) -> List[str]:
    """
    Return a list  of all trix attachments

    e.g. ["http://127.0.0.1:8000/files/543e4f8e-464d-46ec-998b-d2e3e6b07243"]
    """
    attachments = extract_attachments(html)
    return [attachment["url"] for attachment in attachments]
