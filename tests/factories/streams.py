import factory

from data.streams import models


class Stream(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MStream

    name = "Tanzawa"
