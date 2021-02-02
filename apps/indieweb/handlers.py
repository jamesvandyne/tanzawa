import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from files.utils import extract_uuid_from_url
from post.models import TPost
from webmention.models import WebMentionResponse

from .models import TWebmention

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WebMentionResponse)
def create_t_webmention(sender, instance, created, raw, using, update_fields, **kwargs):
    uuid = extract_uuid_from_url(instance.response_to)
    try:
        t_post = TPost.objects.get(uuid=uuid)
    except TPost.DoesNotExist:
        logger.info("Webmention received for invalid post %s", uuid)
        return

    try:
        t_webmention = TWebmention.objects.get(
            t_webmention_response=instance, t_post=t_post
        )
        t_webmention.update_microformat_data()
    except TWebmention.DoesNotExist:
        t_webmention = TWebmention.instance_from_webmentionresponse(instance, t_post)
    t_webmention.save()
