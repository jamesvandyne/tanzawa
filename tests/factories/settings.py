import factory

from data.settings import models


class Settings(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MSiteSettings
