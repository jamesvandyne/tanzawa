from django.template.loader import render_to_string

from data.entry import models as entry_models
from data.post import models as post_models


def get_encoded_content(post: post_models.TPost) -> str:
    """
    Get the encoded content suitable for an RSS feed.
    """
    entry = post.ref_t_entry
    e_content = entry.e_content
    context = {"e_content": e_content, "post": post, "entry": entry}
    if entry.is_reply:
        e_content = f"<blockquote>{entry.t_reply.quote}</blockquote>{e_content}"
    elif entry.is_bookmark:
        context["t_bookmark"] = entry.t_bookmark
        e_content = render_to_string("public/feeds/bookmark.html", context=context)
    elif entry.is_checkin:
        context["t_checkin"] = entry.t_checkin
        e_content = render_to_string("public/feeds/checkin.html", context=context)
    try:
        e_content = f"{e_content}<br/>Location: {entry.t_location.summary}"
    except entry_models.TLocation.DoesNotExist:
        pass
    return e_content
