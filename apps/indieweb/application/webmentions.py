import logging

import mf2py
from files.utils import extract_uuid_from_url
from indieweb import models as indieweb_models
from post import models as post_models
from post import queries as post_queries
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
