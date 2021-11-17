from django.db import models
from core.models import TimestampModel


class MPluginQuerySet(models.QuerySet):
    def enabled(self):
        return self.filter(enabled=True)


class MPluginManager(models.Manager):
    pass


class MPlugin(TimestampModel):

    identifier = models.CharField(max_length=255, unique=True)
    enabled = models.BooleanField(default=False)

    objects = MPluginManager.from_queryset(MPluginQuerySet)()
    plugins = MPluginQuerySet.as_manager()

    @classmethod
    def new(cls, identifier: str, enabled: bool):
        return MPlugin.objects.create(identifier=identifier, enabled=enabled)
