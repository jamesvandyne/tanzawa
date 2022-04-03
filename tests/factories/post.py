import factory
from django.utils import timezone
from post import models

# Post Kinds


class NoteKind(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MPostKind
        django_get_or_create = ("key",)

    key = "note"


# Draft Status


class Published(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MPostStatus
        django_get_or_create = ("key",)

    key = "published"


class Draft(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MPostStatus
        django_get_or_create = ("key",)

    key = "draft"


class Post(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TPost

    p_author = factory.SubFactory("tests.factories.User")


class DraftNotePost(Post):
    m_post_kind = factory.SubFactory(NoteKind)
    m_post_status = factory.SubFactory(Draft)


class PublishedNotePost(Post):
    m_post_kind = factory.SubFactory(NoteKind)
    m_post_status = factory.SubFactory(Published)
    dt_published = factory.LazyFunction(timezone.now)
