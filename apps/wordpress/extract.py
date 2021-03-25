from typing import List
from bs4 import BeautifulSoup
from .models import TCategory


def extract_categories(soup: BeautifulSoup) -> List[TCategory]:
    categories = set(soup.find_all("category", attrs={"domain": "category"}))
    return [
        TCategory(name=category.text, nice_name=category.attrs["nicename"])
        for category in categories
    ]
