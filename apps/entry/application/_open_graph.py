from dataclasses import asdict, dataclass, field
from typing import Optional

from entry import models
from files.domain import images
from meta import views as meta_views


@dataclass
class OpenGraphImage:
    url: str
    type: str
    width: Optional[int] = field(default=None)
    height: Optional[int] = field(default=None)
    alt: str = field(default="")


def get_open_graph_meta_for_entry(request, entry: models.TEntry) -> meta_views.Meta:
    """
    This function returns open graph meta data for a given entry
    """
    image_meta = _get_image(entry=entry, request=request)
    return meta_views.Meta(
        use_twitter=True,
        use_og=True,
        use_fb=True,
        url=request.build_absolute_uri(entry.t_post.get_absolute_url()),
        title=_get_entry_title(entry=entry),
        image_object=asdict(image_meta) if image_meta else {},
    )


def _get_entry_title(entry: models.TEntry) -> Optional[str]:
    if entry.is_checkin or entry.is_note:
        return None
    return entry.t_post.post_title


def _get_image(entry: models.TEntry, request) -> Optional[OpenGraphImage]:

    if entry.is_checkin or entry.is_note:
        # Notes and checkins might have an image or more associated with them.
        # If so, use the first image for the open graph meta
        image = images.get_representative_image(post=entry.t_post)
        if image:
            formatted_image = image.ref_t_formatted_image.first()
            if formatted_image:
                return OpenGraphImage(
                    url=request.build_absolute_uri(image.get_absolute_url()) + f"?f={formatted_image.mime_type}",
                    type=formatted_image.mime_type,
                    width=formatted_image.width,
                    height=formatted_image.height,
                )
            else:
                return OpenGraphImage(url=request.build_absolute_uri(image.get_absolute_url()), type=image.mime_type)
    return None


def _get_twitter_handle(entry: models.TEntry) -> Optional[str]:
    return (
        entry.t_post.p_author.relme.filter(url__icontains="twitter.com").values_list("display_name", flat=True).first()
    )
