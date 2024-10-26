import ronkyuu
from django.db import transaction
from django.utils import timezone

from data.entry import constants as entry_constants
from data.entry import models as entry_models
from data.indieweb import models as indieweb_models
from data.post import models as post_models


class AlreadySentWebmention(Exception): ...


def post_to_mastodon(t_entry: entry_models.TEntry, entry_absolute_url: str):
    try:
        t_entry.bridgy_publish_url.get(url=entry_constants.BridgySyndicationUrls.mastodon)
    except entry_models.BridgyPublishUrl.DoesNotExist:
        t_entry.new_bridgy_url(entry_constants.BridgySyndicationUrls.mastodon)

    try:
        _send_webmention(
            t_entry=t_entry,
            t_post=t_entry.t_post,
            source=entry_absolute_url,
            target=entry_constants.BridgySyndicationUrls.mastodon,
        )
    except AlreadySentWebmention:
        pass


@transaction.atomic
def _send_webmention(t_entry: entry_models.TEntry, t_post: post_models.TPost, source: str, target: str):
    try:
        t_webmention_send = t_post.ref_t_webmention_send.get(target=target)
    except indieweb_models.TWebmentionSend.DoesNotExist:
        t_webmention_send = indieweb_models.TWebmentionSend(t_post=t_post, target=target, success=False)
    else:
        if t_webmention_send.success:
            # Bridgy only accepts a single webmention per post so we don't spam.
            raise AlreadySentWebmention("Post has already been sent to bridgy.")

    occurred_at = timezone.now()
    response = ronkyuu.sendWebmention(source, target)
    # Per webmention spec: Any 2xx response code MUST be considered a success.
    success = bool(response and 200 <= response.status_code <= 299)
    t_webmention_send.set_send_results(success, occurred_at, response.json())
    if success:
        _create_syndication_url(t_entry, response.headers["location"])


def _create_syndication_url(entry: entry_models.TEntry, syndication_url: str) -> entry_models.TSyndication:
    return entry_models.TSyndication.objects.create(t_entry=entry, url=syndication_url)
