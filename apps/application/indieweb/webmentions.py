import logging
import urllib

import mf2py
import ronkyuu
from bs4 import BeautifulSoup
from django.conf import settings
from django.core import exceptions
from django.utils.timezone import now
from webmention import models as webmention_models

from data.indieweb import models as indieweb_models
from data.indieweb.constants import MPostKinds
from data.post import models as post_models
from data.post.models import TPost
from data.wordpress import models as wp_models
from domain.files.utils import extract_uuid_from_url
from domain.indieweb import utils
from domain.indieweb import webmention as webmention_domain
from domain.post import queries as post_queries

logger = logging.getLogger(__name__)


def create_moderation_record_for_webmention(webmention: webmention_models.WebMentionResponse) -> None:
    """
    Called when a webmention is created. Look up the post that the webmention is referring to
    and create/update a TWebmention instance for moderation.
    """

    t_post = _determine_post_for_url(webmention.response_to)
    if t_post is None:
        return None

    microformat_data = _extract_microformat_data(webmention=webmention)

    try:
        t_webmention = webmention_domain.get_webmention(webmention_id=webmention.pk, t_post_id=t_post.pk)
        t_webmention.reset_moderation(microformat_data=microformat_data)
    except indieweb_models.TWebmention.DoesNotExist:
        indieweb_models.TWebmention.new(
            t_webmention_response=webmention, t_post=t_post, microformat_data=microformat_data
        )


def _get_post_by_uuid(url: str) -> TPost | None:
    """
    Return a post by extracting a uuid from its url.
    """
    uuid = extract_uuid_from_url(url)
    try:
        return post_queries.get_t_post_by_uuid(uuid)
    except (exceptions.ValidationError, post_models.TPost.DoesNotExist):
        return None


def _get_post_by_wordpress_path(url: str) -> TPost | None:
    """
    Return post by cross referencing urls from a wordpress import.
    """
    path = urllib.parse.urlparse(url).path

    try:
        wordpress_post = wp_models.TWordpressPost.objects.get(path=path)
    except (wp_models.TWordpressPost.DoesNotExist, wp_models.TWordpressPost.MultipleObjectsReturned):
        return None
    else:
        return wordpress_post.t_post


def _determine_post_for_url(url: str) -> TPost | None:
    """
    Determine a post for a given url.
    """
    t_post = _get_post_by_uuid(url)
    if t_post:
        return t_post
    return _get_post_by_wordpress_path(url)


def send_webmention(request, t_post: TPost, e_content: str) -> list[indieweb_models.TWebmentionSend]:
    source_url = request.build_absolute_uri(t_post.get_absolute_url())
    mentions = ronkyuu.findMentions(source_url, exclude_domains=settings.ALLOWED_HOSTS, content=e_content)

    t_webmention_sends: list[indieweb_models.TWebmentionSend] = []
    refs: set[str] = mentions["refs"]
    if t_post.m_post_kind.key == MPostKinds.reply:
        refs.add(t_post.ref_t_entry.t_reply.u_in_reply_to)

    for target in refs:
        if target == source_url:
            continue

        wm_status, wm_url = ronkyuu.discoverEndpoint(target, test_urls=False)
        if wm_url is not None and wm_status == 200:
            try:
                t_webmention_send = t_post.ref_t_webmention_send.get(target=target)
            except indieweb_models.TWebmentionSend.DoesNotExist:
                t_webmention_send = indieweb_models.TWebmentionSend(t_post=t_post, target=target, success=False)

            response = ronkyuu.sendWebmention(source_url, target, wm_url)
            t_webmention_send.dt_sent = now()
            # Per webmention spec: Any 2xx response code MUST be considered a success.
            if response and 200 <= response.status_code <= 299:
                t_webmention_send.success = True
            else:
                t_webmention_send.success = False
            t_webmention_send.save()
            t_webmention_sends.append(t_webmention_send)

    return t_webmention_sends


def moderate_webmention(t_web_mention: indieweb_models.TWebmention, approval: bool) -> None:
    t_web_mention.set_approval(approved=approval)


def _extract_microformat_data(*, webmention: webmention_models.WebMentionResponse):
    # make sure that we encode emoji and such properly
    cleaned_response = webmention.response_body
    parsed = mf2py.parse(doc=cleaned_response)
    mf_data = utils.interpret_comment(
        parsed,
        webmention.source,
        [webmention.response_to],
    )
    return mf_data


def _find_a_tags(e_content: str) -> list[str]:
    soup = BeautifulSoup(e_content, "html.parser")
    return [a["href"] for a in soup.select("a")]
