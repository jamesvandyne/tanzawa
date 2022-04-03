from data.entry import models as entry_models
from post.models import TPost


def get_encoded_content(post: TPost) -> str:
    """
    Get the encoded content suitable for an RSS feed.
    """
    entry = post.ref_t_entry
    e_content = entry.e_content

    if entry.is_reply:
        e_content = f"<blockquote>{entry.t_reply.quote}</blockquote>{e_content}"
    elif entry.is_bookmark:
        t_bookmark = entry.t_bookmark
        e_content = (
            f"Bookmark: "
            f'<a href="{t_bookmark.u_bookmark_of}"'
            f">{t_bookmark.title or t_bookmark.u_bookmark_of}</a>"
            f"<blockquote>{t_bookmark.quote}</blockquote>{e_content}"
        )
    elif entry.is_checkin:
        e_content = f"{post.post_title}<br/>{e_content}"
    try:
        e_content = f"{e_content}<br/>Location: {entry.t_location.summary}"
    except entry_models.TLocation.DoesNotExist:
        pass
    return e_content
