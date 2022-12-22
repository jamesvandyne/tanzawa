from typing import Any


class UnknownContentType(Exception):
    pass


class ContentType:
    JSON = "application/json"
    FORM_URLENCODED = "application/x-www-form-urlencoded"
    MULTIPART_FORM = "multipart/form-data"


def normalize_request(*, content_type: str, post_data, request_data) -> dict[str, Any]:
    """
    Normalize form posts and json requests into a microformat2 shaped object.
    """
    base_content_type = content_type.split(";")[0]
    normalize_func = normalize.get(base_content_type)
    if not normalize_func:
        raise UnknownContentType()

    if base_content_type == ContentType.JSON:
        request_body = request_data
    else:
        request_body = post_data

    body = normalize_func(request_body)
    body["type"] = body["type"][0]  # type is a list but needs to be a string
    return body


def _form_to_mf2(post):
    """Convert a form post to microformat2 shaped object."""
    properties = {}
    for key in post.keys():
        if key.endswith("[]"):
            key = key[:-2]
        if key == "access_token":
            continue
        properties[key] = post.getlist(key) + post.getlist(key + "[]")
    mf = {"type": [f'h-{post.get("h", "")}'], "properties": properties}
    return __normalize_properties_to_underscore(mf)


def __normalize_properties_to_underscore(data: dict[str, Any]) -> dict[str, Any]:
    """Converts microformat2 style property keys from hyphen to underscores."""
    properties = {}
    for key, value in data.get("properties", {}).items():
        properties[key.replace("-", "_")] = value
    return {"type": data["type"], "properties": properties}


def _normalize_properties(data: dict[str, Any]) -> dict[str, Any]:
    h_entry = __normalize_properties_to_underscore(data)
    return h_entry


normalize = {
    ContentType.JSON: _normalize_properties,
    ContentType.FORM_URLENCODED: _form_to_mf2,
    ContentType.MULTIPART_FORM: _form_to_mf2,
}
