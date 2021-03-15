import json
import re
import requests
from dataclasses import dataclass
from itertools import chain
import logging
from PIL import Image
from bs4.element import Tag
from typing import List, Optional, Union
import base64
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from mf2util import (
    _find_all_entries,
    classify_comment,
    get_plain_text,
    interpret_entry,
    parse_author,
)
from files.forms import MediaUploadForm
from files.models import TFile
from files.images import bytes_as_upload_image


IMG_DATA_PATTERN = re.compile(
    r"^data:(?P<mime_type>.+);(?P<encoding>.+),(?P<image_data>.+)$"
)

logger = logging.getLogger(__name__)


@dataclass
class DataImage:
    image_data: Union[str, bytes]  # encoded data
    mime_type: str  # image/png
    encoding: str  # base64
    tag: Optional[Tag]  # original img tag

    def decode(self) -> Optional[bytes]:
        if self.encoding == "base64":
            return base64.b64decode(self.image_data)
        elif self.encoding == "none":
            return self.image_data
        else:
            logger.info("Unknown encoding. Unable decode image")
        return None


def find_entry(parsed, types, target_url):
    """Find the first comment, reply, like of that matches our current post

    Some contain multiple webmentions (items). mf2py by default returns the first item, regardless
    if the like-of, in-reply-to, or repost-of url matches our target url or not.

    Filter the items and return the one that has a url match
    """
    entry = None
    for entry in _find_all_entries(parsed, types, False):
        entry_urls = chain.from_iterable(
            entry.get("properties", {}).get(prop, [])
            for prop in ("like-of", "in-reply-to", "repost-of")
        )
        if target_url in entry_urls:
            return entry
    # default to return first entry or None
    return entry


def interpret_comment(
    parsed,
    source_url,
    target_urls,
    base_href=None,
    want_json=False,
    fetch_mf2_func=None,
):
    """The same as mf2py, except it filters the entry by the target url"""
    item = find_entry(parsed, ["h-entry"], target_urls[0])
    if item:
        result = interpret_entry(
            parsed,
            source_url,
            base_href=base_href,
            hentry=item,
            want_json=want_json,
            fetch_mf2_func=fetch_mf2_func,
        )
        if result:
            result["comment_type"] = classify_comment(parsed, target_urls)
            rsvp = get_plain_text(item["properties"].get("rsvp"))
            if rsvp:
                result["rsvp"] = rsvp.lower()

            invitees = item["properties"].get("invitee")
            if invitees:
                result["invitees"] = [parse_author(inv) for inv in invitees]

        return result


def extract_base64_images(soup: BeautifulSoup) -> List[DataImage]:
    attachments = []
    for img in soup.select(r"img[src^=data\:]"):
        data = IMG_DATA_PATTERN.match(img["src"])
        if data:
            attachments.append(DataImage(tag=img, **data.groupdict()))
    return attachments


def download_image(url: str) -> Optional[DataImage]:
    response = requests.get(url)
    if response.status_code == 200:
        return DataImage(
            image_data=response.content,
            mime_type=response.headers["Content-Type"],
            encoding="none",
            tag=None,
        )
    return None


def save_and_get_tag(request, image: DataImage) -> Optional[BeautifulSoup]:
    # convert base64 embeded image to a SimpleFileUpload object
    upload_file, width, height = bytes_as_upload_image(image.decode(), image.mime_type)
    if not upload_file:
        return None
    # Save to disk
    file_form = MediaUploadForm(files={"file": upload_file})
    if file_form.is_valid():
        t_file = file_form.save()
        img_src = request.build_absolute_uri(t_file.get_absolute_url())
        context = {
            "mime": image.mime_type,
            "src": img_src,
            "width": width,
            "height": height,
            "trix_attachment_data": json.dumps(
                {
                    "contentType": image.mime_type,
                    "filename": upload_file.name,
                    "filesize": t_file.file.size,
                    "height": height,
                    "href": f"{img_src}?content-disposition=attachment",
                    "url": img_src,
                    "width": width,
                }
            ),
        }
        # Render as trix
        return BeautifulSoup(
            render_to_string("trix/figure.html", context), "html.parser"
        )
    logger.info("unable to save image: %s", file_form.errors)
    return None


def render_attachment(request, attachment: TFile) -> str:
    """
    Render an attachment to be inserted into a trix editor
    """
    img = Image.open(attachment.file)
    img_src = request.build_absolute_uri(attachment.get_absolute_url())
    context = {
        "mime": attachment.mime_type,
        "src": img_src,
        "width": img.width,
        "height": img.height,
        "trix_attachment_data": json.dumps(
            {
                "contentType": attachment.mime_type,
                "filename": attachment.filename,
                "filesize": attachment.file.size,
                "height": img.height,
                "href": f"{img_src}?content-disposition=attachment",
                "url": img_src,
                "width": img.width,
            }
        ),
    }
    return render_to_string("trix/figure.html", context)
