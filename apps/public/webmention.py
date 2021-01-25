from datetime import datetime
from typing import Dict, List, Union
import mf2py
import mf2util
from post.models import TPost
from webmention.models import WebMentionResponse
from indieweb.constants import MPostKinds


def get_webmentions(t_post: TPost) -> Dict[str, List[Dict[str, Union[str, datetime, Dict[str, str], List[str]]]]]:
    webmentions = WebMentionResponse.objects.filter(response_to__endswith=t_post.get_absolute_url())

    ret = {
        MPostKinds.like: [],
        MPostKinds.reply: [],
        MPostKinds.repost: [],
        MPostKinds.rsvp: [],
        'link': [],
    }

    for wm in webmentions:
        parsed = mf2py.parse(doc=wm.response_body)
        comment = mf2util.interpret_comment(parsed, wm.source,  [wm.response_to])

        obj = {
            "author": {
                "name": comment.get('author', {}).get('name')
            }
        }

        if not comment['comment_type']:
            ret['link'].append(comment)
            continue

        # like, reply, repost
        for comment_type in comment['comment_type']:
            ret[comment_type].append(comment)
    return ret
