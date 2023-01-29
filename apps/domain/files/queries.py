from django.db.models import QuerySet

from core.constants import Visibility
from data.files import models as file_models
from data.indieweb.constants import MPostStatuses
from data.post import models as post_models


def get_public_photos(limit: int = 10) -> QuerySet[file_models.TFile]:
    """
    Return a queryset of public photos.
    """
    qs = (
        file_models.TFile.objects.filter(mime_type__startswith="image")
        .filter(posts__m_post_status__key=MPostStatuses.published)
        .exclude(posts__visibility=Visibility.UNLISTED)
        .order_by("-posts__dt_published")
    )
    return qs[:limit]


def get_representative_image(post: post_models.TPost) -> file_models.TFile | None:
    """
    Return the first image in a post that's used as the representative image.
    """
    return post.files.filter(mime_type__startswith="image").first()
