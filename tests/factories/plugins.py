import factory
import faker
from data.plugins import models

fake = faker.Faker()


class MPlugin(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MPlugin

    enabled = True
