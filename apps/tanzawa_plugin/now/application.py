from django.db import transaction

from data.files import models as files_models
from domain.files import utils as files_utils
from domain.trix import queries as trix_queries

from . import models


@transaction.atomic
def update_now(*, t_now: models.TNow, content: str) -> None:
    """
    Update A Now Page.
    """
    urls = trix_queries.extract_attachment_urls(content)
    file_attachment_uuids = [files_utils.extract_uuid_from_url(url) for url in urls]
    matching_files = files_models.TFile.objects.filter(uuid__in=file_attachment_uuids)

    t_now.set_content(content)
    t_now.files.set(matching_files)
