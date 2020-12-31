import logging
from typing import Optional

from indieweb import constants
from post.models import MPostKind


def determine_post_kind(data) -> Optional[str]:
    try:
        post_kind = MPostKind.objects.get(key=data.get("post-kind"))
    except MPostKind.DoesNotExist:
        post_kind = None
        logging.info(f"post-status: {data.get('post-kind')} doesn't exist")
    return post_kind or MPostKind.objects.get(key=constants.MPostKinds.article)