from typing import Optional

from entry import models
from meta import views as meta_views


def get_open_graph_meta_for_entry(request, entry: models.TEntry) -> meta_views.Meta:
    """
    This function returns open graph meta data for a given entry
    """
    return meta_views.Meta(
        use_twitter=True,
        use_og=True,
        use_fb=True,
        url=request.build_absolute_uri(entry.t_post.get_absolute_url()),
        title=_get_entry_title(entry=entry),
    )


def _get_entry_title(entry: models.TEntry) -> Optional[str]:
    if entry.is_checkin or entry.is_note:
        return None
    return entry.t_post.post_title
