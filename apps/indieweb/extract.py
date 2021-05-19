import extruct
import requests
from bs4 import BeautifulSoup
from typing import Optional
import mf2util
from dataclasses import dataclass


@dataclass
class LinkedPageAuthor:
    name: Optional[str]
    url: Optional[str]
    photo: Optional[str]  # url


@dataclass
class LinkedPage:
    url: str
    title: str
    description: str
    author: Optional[LinkedPageAuthor]


def extract_title(soup: BeautifulSoup) -> str:
    """Extract the default page title. Prefer opengraph title if it exists."""
    og_title = soup.find("meta", property="og:title")
    default_title = soup.title.text if soup.title else ""
    return og_title["content"] if og_title else default_title


def extract_description(soup: BeautifulSoup) -> str:
    """Extract the default page title"""
    desc = soup.find("meta", property="og:description")
    return desc["content"] if desc else ""


def extract_reply_details_from_url(url: str) -> Optional[LinkedPage]:

    response = requests.get(url)
    if response.status_code != 200:
        return

    data = extruct.extract(response.text)
    title_keys = ["headline", "title", "name"]
    desc_keys = ["description", "summary"]
    soup = BeautifulSoup(response.text, "html.parser")
    linked_page = LinkedPage(
        url=url,
        title=extract_title(soup) or url,
        description=extract_description(soup),
        author=LinkedPageAuthor(name="", url="", photo=""),
    )

    if data["microformat"]:
        entry = mf2util.interpret_entry({"items": data["microformat"]}, source_url=url)
        entry_soup = BeautifulSoup(entry.get("content", ""), "html.parser")
        description = entry_soup.text[:255].strip()
        linked_page.title = entry.get("name") or linked_page.title or description[:128].strip()
        linked_page.description = description
        linked_page.author = LinkedPageAuthor(
            name=entry.get("author", {}).get("name", ""),
            url=entry.get("author", {}).get("url", ""),
            photo=entry.get("author", {}).get("image"),
        )
        return linked_page
    for schema in data["json-ld"]:
        linked_page.title = next(schema[key] for key in title_keys if key in schema) or linked_page.title
        linked_page.description = next(schema[key] for key in desc_keys if key in schema) or linked_page.description
        linked_page.author = (
            LinkedPageAuthor(
                name=schema["author"][0].get("name", ""),
                url=schema["author"][0].get("url", ""),
                photo=schema["author"][0].get("image"),
            )
            if "author" in schema
            else None
        )
        return linked_page
    return linked_page
