import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from post.models import TPost
from webmention.models import WebMentionResponse

from .models import TWebmention

logger = logging.getLogger(__name__)


@receiver(post_save, sender=WebMentionResponse)
def create_t_webmention(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        uuid = instance.response_to[-36:]
        try:
            t_post = TPost.objects.get(uuid=uuid)
            t_webmention = TWebmention.instance_from_webmentionresponse(
                instance, t_post
            )
            t_webmention.save()
        except TPost.DoesNotExist:
            logger.info("Webmention received for invalid post %s", uuid)
