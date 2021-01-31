from itertools import chain

from mf2util import (_find_all_entries, classify_comment, get_plain_text,
                     interpret_entry, parse_author)


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
