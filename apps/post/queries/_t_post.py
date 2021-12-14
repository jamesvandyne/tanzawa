from .. import models


def get_t_post_by_uuid(uuid: str) -> models.TPost:
    return models.TPost.objects.get(uuid=uuid)
