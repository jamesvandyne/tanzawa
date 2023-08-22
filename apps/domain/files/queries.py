from dataclasses import dataclass

from django.db.models import Q, QuerySet
from PIL import Image, UnidentifiedImageError

from core.constants import Visibility
from data.files import constants as file_constants
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


@dataclass(frozen=True)
class Size:
    width: int
    height: int


def get_size_for_file(t_file: file_models.TFile) -> Size:
    """
    Return the size for a given file.
    """
    try:
        with Image.open(t_file.file) as image:
            return Size(width=image.width, height=image.height)
    except UnidentifiedImageError:
        # Return a fixed size if case we upload a PDF or some non-Image file.
        return Size(width=600, height=600)


def can_process_file(mime_type: str | None) -> bool:
    """
    Return if we can process a mime type or not.
    """
    return mime_type in file_constants.PICTURE_FORMATS.keys()


def get_processed_file(
    t_file: file_models.TFile, mime_type: str | None = None, longest_edge: int | None = None
) -> file_models.TFormattedImage | None:
    """
    Get a pre-processed file (thumbnail etc..) for a given file.
    """
    qs = t_file.ref_t_formatted_image.all()
    if mime_type:
        qs = qs.filter(mime_type=mime_type)
    if longest_edge:
        qs = qs.filter(Q(width=longest_edge) | Q(height=longest_edge))
    else:
        # Ensure we do not return a thumbnail sized photo when requesting the original without a
        # specified size as it causes photos to become blurry.
        original_size = get_size_for_file(t_file)
        qs = qs.filter(Q(width=original_size.width) | Q(height=original_size.height))
    return qs.first()


def get_image_url(request, t_file: file_models.TFile) -> str:
    img_url = request.build_absolute_uri(t_file.get_absolute_url())
    return img_url
