from data.indieweb.constants import MPostKinds, MPostStatuses
from data.post import models


def get_t_post_by_uuid(uuid: str) -> models.TPost:
    return models.TPost.objects.get(uuid=uuid)


def get_post_status(status: MPostStatuses) -> models.MPostStatus:
    return models.MPostStatus.objects.get(key=status)


def get_post_kind(kind: MPostKinds) -> models.MPostKind:
    return models.MPostKind.objects.get(key=kind)
