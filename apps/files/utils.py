def extract_uuid_from_url(url: str) -> str:
    """
    input: http://127.0.0.1:8000/files/543e4f8e-464d-46ec-998b-d2e3e6b07243
    output: 543e4f8e-464d-46ec-998b-d2e3e6b07243
    """
    return url.split("/")[-1]
