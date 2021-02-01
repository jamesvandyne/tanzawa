from bs4 import BeautifulSoup
from typing import List
from webmentiontools.send import WebmentionSend
from post.models import TPost
from .models import TWebmentionSend
from django.utils.timezone import now


def find_a_tags(e_content: str) -> List[str]:
    soup = BeautifulSoup(e_content, "html.parser")
    return [a['href'] for a in soup.select("a")]


def send_webmention(request, t_post: TPost, target: str) -> TWebmentionSend:
    try:
        t_webmention_send = t_post.ref_t_webmention_send.get(target=target)
    except  TWebmentionSend.DoesNotExist:
        t_webmention_send = TWebmentionSend(t_post=t_post, target=target, success=False)
    source = request.build_absolute_uri(t_post.get_absolute_url())

    mention = WebmentionSend(source, target)
    t_webmention_send.dt_sent = now()
    t_webmention_send.success = mention.send()
    t_webmention_send.save()
    return t_webmention_send
