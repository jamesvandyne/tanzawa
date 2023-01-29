from data.files import models as file_models
from django.db.models import QuerySet
from data.indieweb.constants import MPostStatuses

from core.constants import Visibility


def get_public_photos(limit: int = 10) -> QuerySet[file_models.TFile]:
    qs = (
        file_models.TFile.objects.filter(mime_type__startswith="image")
        .filter(posts__m_post_status__key=MPostStatuses.published)
        .exclude(posts__visibility=Visibility.UNLISTED)
        .order_by("-posts__dt_published")
    )
    return qs[:limit]
