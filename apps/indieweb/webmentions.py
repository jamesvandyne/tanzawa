from typing import List, Set

import ronkyuu
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils.timezone import now
from post.models import TPost
from indieweb.constants import MPostKinds
from .models import TWebmentionSend


def find_a_tags(e_content: str) -> List[str]:
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
