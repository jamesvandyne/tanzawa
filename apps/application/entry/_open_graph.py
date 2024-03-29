from dataclasses import dataclass, field

from django import urls
from meta import views as meta_views

from data.entry import models
from domain.files import queries


@dataclass
class OpenGraphImage:
    url: str
    secure_url: str
    type: str
    width: int | None = field(default=None)
    height: int | None = field(default=None)
    alt: str = field(default="")


def get_open_graph_meta_for_entry(request, entry: models.TEntry) -> meta_views.Meta:
    """
    This function returns open graph meta data for a given entry
    """
    image_meta = _get_image(entry=entry, request=request)
    return meta_views.Meta(
        url=request.build_absolute_uri(entry.t_post.get_absolute_url()).replace("https:", "http:"),
        secure_url=request.build_absolute_uri(entry.t_post.get_absolute_url()),
        title=_get_entry_title(entry=entry),
        image=image_meta.secure_url if image_meta else None,
        twitter_type="summary_large_image" if image_meta else "summary",
        twitter_creator=_get_twitter_handle(entry),
    )


def _get_entry_title(entry: models.TEntry) -> str | None:
    if entry.is_checkin or entry.is_note:
        return None
    return entry.t_post.post_title


def _get_image(entry: models.TEntry, request) -> OpenGraphImage | None:
    if entry.is_checkin or entry.is_note or entry.is_article:
        # Notes and checkins might have an image or more associated with them.
        # If so, use the first image for the open graph meta
        image = queries.get_representative_image(post=entry.t_post)
        if image:
            formatted_image = image.ref_t_formatted_image.first()
            if formatted_image:
                return OpenGraphImage(
                    url=request.build_absolute_uri(image.get_absolute_url()) + f"?f={formatted_image.mime_type}",
                    secure_url=request.build_absolute_uri(image.get_absolute_url()) + f"?f={formatted_image.mime_type}",
                    type=formatted_image.mime_type,
                    width=formatted_image.width,
                    height=formatted_image.height,
                )
            else:
                return OpenGraphImage(
                    url=request.build_absolute_uri(image.get_absolute_url()),
                    secure_url=request.build_absolute_uri(image.get_absolute_url()),
                    type=image.mime_type,
                )
        if activity := entry.activities.first():
            return OpenGraphImage(
                url=request.build_absolute_uri(urls.reverse("plugin_exercise:activity_route", args=[activity.pk])),
                secure_url=request.build_absolute_uri(
                    urls.reverse("plugin_exercise:activity_route", args=[activity.pk])
                ),
                type="image/png",
                width=1200,
                height=630,
            )

    return None


def _get_twitter_handle(entry: models.TEntry) -> str | None:
    return (
        entry.t_post.p_author.relme.filter(url__icontains="twitter.com").values_list("display_name", flat=True).first()
    )
