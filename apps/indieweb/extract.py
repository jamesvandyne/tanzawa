import extruct
import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any
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


def extract_reply_details_from_url(url: str) -> Optional[LinkedPage]:

    response = requests.get(url)
    data = extruct.extract(response.text)
    title_keys = ["headline", "title", "name"]
    desc_keys = ["description", "summary"]
    for schema in data["json-ld"]:
        return LinkedPage(
            url=url,
            title=next(schema[key] for key in title_keys if key in schema) or "",
            description=next(schema[key] for key in desc_keys if key in schema) or "",
            author=LinkedPageAuthor(
                name=schema["author"][0].get("name", ""),
                url=schema["author"][0].get("url", ""),
                photo=schema["author"][0].get("image"),
            )
            if "author" in schema
            else None,
        )

    if data["microformat"]:
        entry = mf2util.interpret_entry({"items": data["microformat"]}, source_url=url)
        soup = BeautifulSoup(entry.get("content", ""), "html.parser")
        description = soup.text[:255].strip()
        return LinkedPage(
            url=entry.get("url", ""),
            title=entry.get("name") or description[:128].strip(),
            description=description,
            author=LinkedPageAuthor(
                name=entry["author"].get("name", ""),
                url=entry["author"].get("url", ""),
                photo=entry["author"].get("image"),
            )
        )
