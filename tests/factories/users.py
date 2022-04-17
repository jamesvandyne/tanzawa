import factory
import faker
from django.contrib.auth import models as auth_models

fake = faker.Faker()


class User(factory.django.DjangoModelFactory):
    class Meta:
        model = auth_models.User

    username = factory.LazyFunction(fake.pystr)
