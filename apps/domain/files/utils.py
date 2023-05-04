import re

UUID_REGEX = re.compile(r"[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}", re.IGNORECASE)


def extract_uuid_from_url(url: str) -> str:
    """
    input: http://127.0.0.1:8000/files/543e4f8e-464d-46ec-998b-d2e3e6b07243
    output: 543e4f8e-464d-46ec-998b-d2e3e6b07243
    """
    if match := UUID_REGEX.search(url):
        return match[0]
    raise ValueError("UUID not found")
