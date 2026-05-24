import factory
import uuid
import faker
from django.contrib.auth import models as auth_models

fake = faker.Faker()


class User(factory.django.DjangoModelFactory):
    class Meta:
        model = auth_models.User

    username = factory.LazyFunction(lambda: fake.pystr() + '_' + uuid.uuid4().hex[:8])
    email = "james@example.test"
