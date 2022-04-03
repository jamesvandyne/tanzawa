import factory
from data.entry import models


class StatusEntry(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TEntry

    p_name = ""
    p_summary = "Content here"
    e_content = "<h1>Content here</h1>"
    t_post = factory.SubFactory("tests.factories.StatusPost")
