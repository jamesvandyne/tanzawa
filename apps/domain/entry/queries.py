import bs4

from data.entry import constants as entry_constants
from data.entry import models as entry_models
from domain.files import utils as file_utils
from domain.trix import queries as trix_queries


def get_summary(e_content: str, max_length=255) -> str:
    """
    Return a plain text summary from an html string.
    """
    soup = bs4.BeautifulSoup(e_content, features="html.parser")

    if max_length:
        return soup.text[:max_length].strip()
    return soup.text.strip()


def get_attachment_identifiers_in_content(e_content: str) -> list[str]:
    """
    Return a list of file attachments referenced in the content body.
    """
    urls = trix_queries.extract_attachment_urls(e_content)
    return [file_utils.extract_uuid_from_url(url) for url in urls]


def is_syndicated_to_mastodon(entry: entry_models.TEntry) -> bool:
    """
    Determine if an entry has been sent to Mastodon with Bri.gy.
    """
    return _get_bridgy_webmention(entry, target=entry_constants.BridgySyndicationUrls.mastodon).exists()


def mastodon_syndication_url(entry: entry_models.TEntry) -> str | None:
    mastodon_wm = _get_bridgy_webmention(entry, target=entry_constants.BridgySyndicationUrls.mastodon)
    for wm in mastodon_wm:
        return wm.response_body.get("url")
    return None


def is_syndicated_to_bluesky(entry: entry_models.TEntry) -> bool:
    """
    Determine if an entry has been sent to Bluesky with Bri.gy.
    """
    return _get_bridgy_webmention(entry, target=entry_constants.BridgySyndicationUrls.bluesky).exists()


def bluesky_syndication_url(entry: entry_models.TEntry) -> str | None:
    mastodon_wm = _get_bridgy_webmention(entry, target=entry_constants.BridgySyndicationUrls.bluesky)
    for wm in mastodon_wm:
        return wm.response_body.get("url")
    return None


def _get_bridgy_webmention(entry: entry_models.TEntry, target: entry_constants.BridgySyndicationUrls):
    return entry.t_post.ref_t_webmention_send.filter(target=target, success=True)
