import factory
from data.trips import models


class Trip(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TTrip

    name = "Beach Trip"
    p_author = factory.SubFactory("tests.factories.User")
