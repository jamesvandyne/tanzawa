from typing import Iterable

from indieweb import models


def get_relme() -> Iterable[models.TRelMe]:
    """Get all relme records"""
    return models.TRelMe.objects.all()
