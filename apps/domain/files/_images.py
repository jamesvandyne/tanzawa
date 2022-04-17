from typing import Optional

from data.files import models
from data.post import models as post_models


def get_representative_image(post: post_models.TPost) -> Optional[models.TFile]:
    return post.files.filter(mime_type__startswith="image").first()
