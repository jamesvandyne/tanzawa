import factory
from django.utils import timezone

from data.post import models

# Post Kinds


class _MPostKind(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MPostKind
        django_get_or_create = ("key",)


class NoteKind(_MPostKind):
    key = "note"


class ArticleKind(_MPostKind):
    key = "article"


class ReplyKind(_MPostKind):
    key = "reply"


class BookmarkKind(_MPostKind):
    key = "bookmark"


class CheckinKind(_MPostKind):
    key = "checkin"


# Draft Status


class _MPostStatus(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MPostStatus
        django_get_or_create = ("key",)


class Published(_MPostStatus):
    key = "published"


class Draft(_MPostStatus):
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


class PublishedArticlePost(Post):
    m_post_kind = factory.SubFactory(ArticleKind)
    m_post_status = factory.SubFactory(Published)
    dt_published = factory.LazyFunction(timezone.now)


class PublishedBookmarkPost(Post):
    m_post_kind = factory.SubFactory(BookmarkKind)
    m_post_status = factory.SubFactory(Published)
    dt_published = factory.LazyFunction(timezone.now)


class PublishedReplyPost(Post):
    m_post_kind = factory.SubFactory(ReplyKind)
    m_post_status = factory.SubFactory(Published)
    dt_published = factory.LazyFunction(timezone.now)


class PublishedCheckinPost(Post):
    m_post_kind = factory.SubFactory(CheckinKind)
    m_post_status = factory.SubFactory(Published)
    dt_published = factory.LazyFunction(timezone.now)
