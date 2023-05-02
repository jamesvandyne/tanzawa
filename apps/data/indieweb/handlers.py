import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from webmention import models as webmention_models

from application.indieweb import webmentions

logger = logging.getLogger(__name__)


@receiver(post_save, sender=webmention_models.WebMentionResponse)
def create_t_webmention(sender, instance, created, raw, using, update_fields, **kwargs):
    webmentions.create_moderation_record_for_webmention(instance)
