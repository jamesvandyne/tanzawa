from django.db.models import TextChoices


class BridgySyndicationUrls(TextChoices):
    mastodon = "https://brid.gy/publish/mastodon"
