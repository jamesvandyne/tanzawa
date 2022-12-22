import bs4

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
