import pytest
from django.core.management import call_command
from django.db import connection
from model_bakery import baker

from data.indieweb.constants import MPostStatuses


@pytest.fixture
def client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def m_post_kinds():
    from data.post.models import MPostKind

    return MPostKind.objects.all()


@pytest.fixture
def m_post_kind(m_post_kinds):
    return m_post_kinds[0]  # note


@pytest.fixture
def published_status():
    from data.post.models import MPostStatus

    return MPostStatus.objects.get(key=MPostStatuses.published)


@pytest.fixture
def draft_status():
    from data.post.models import MPostStatus

    return MPostStatus.objects.get(key=MPostStatuses.draft)


@pytest.fixture
def user():
    return baker.make(
        "User",
        username="jamesvandyne",
        first_name="James",
        last_name="Van Dyne",
        email="james@example.test",
    )


@pytest.fixture
def t_post(m_post_kind, published_status, user):
    from datetime import datetime

    return baker.make(
        "post.TPost",
        m_post_status=published_status,
        m_post_kind=m_post_kind,
        p_author=user,
        dt_published=datetime.now(),
        uuid="90a0027d-9c74-44e8-895c-6d5611f8eca5",
    )


@pytest.fixture
def factory():
    from tests import factories

    return factories


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    with django_db_blocker.unblock():
        with connection.cursor() as c:
            # Spatalite5 and sqlite 3.36 are incompatible with each other.
            # Force creation of the spatial metadata before running migrations.
            # This should be a "temporary" fix so tests can run on CI.
            # refs: https://code.djangoproject.com/ticket/32935
            c.execute("SELECT InitSpatialMetaData(1);")
        call_command("migrate", interactive=False)
