import logging
from typing import List, Set

import mf2py
import ronkyuu
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils.timezone import now
from files.utils import extract_uuid_from_url
from indieweb import models as indieweb_models
from indieweb.constants import MPostKinds
from indieweb.models import TWebmentionSend
from post import models as post_models
from post import queries as post_queries
from post.models import TPost
from webmention import models as webmention_models

from .. import queries as indieweb_queries
from .. import utils

logger = logging.getLogger(__name__)


def create_moderation_record_for_webmention(webmention: webmention_models.WebMentionResponse) -> None:
    """
    Called when a webmention is created. Look up the post that the webmention is referring to
    and create/update a TWebmention instance for moderation.
    """

    uuid = extract_uuid_from_url(webmention.response_to)
    try:
        t_post = post_queries.get_t_post_by_uuid(uuid)
    except post_models.TPost.DoesNotExist:
        logger.info("Webmention received for invalid post %s", uuid)
        return

    microformat_data = _extract_microformat_data(webmention=webmention)

    try:
        t_webmention = indieweb_queries.get_webmention(webmention_id=webmention.pk, t_post_id=t_post.pk)
        t_webmention.reset_moderation(microformat_data=microformat_data)
    except indieweb_models.TWebmention.DoesNotExist:
        indieweb_models.TWebmention.new(
            t_webmention_response=webmention, t_post=t_post, microformat_data=microformat_data
        )


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


def _find_a_tags(e_content: str) -> List[str]:
    soup = BeautifulSoup(e_content, "html.parser")
    return [a["href"] for a in soup.select("a")]


def send_webmention(request, t_post: TPost, e_content: str) -> List[TWebmentionSend]:
    source_url = request.build_absolute_uri(t_post.get_absolute_url())
    mentions = ronkyuu.findMentions(source_url, exclude_domains=settings.ALLOWED_HOSTS, content=e_content)

    t_webmention_sends: List[TWebmentionSend] = []
    refs: Set[str] = mentions["refs"]
    if t_post.m_post_kind.key == MPostKinds.reply:
        refs.add(t_post.ref_t_entry.t_reply.u_in_reply_to)

    for target in refs:
        if target == source_url:
            continue

        wm_status, wm_url = ronkyuu.discoverEndpoint(target, test_urls=False)
        if wm_url is not None and wm_status == 200:

            try:
                t_webmention_send = t_post.ref_t_webmention_send.get(target=target)
            except TWebmentionSend.DoesNotExist:
                t_webmention_send = TWebmentionSend(t_post=t_post, target=target, success=False)

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
