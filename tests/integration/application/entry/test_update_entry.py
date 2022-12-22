import pytest
from application.entry import update_entry
from data.entry import models as entry_models

from tests import factories


@pytest.mark.django_db
class TestUpdateEntry:
    def test_clears_location(self) -> None:
        """
        Given an entry with a location
        Expect updates without a location will remove the location
        """

        entry = factories.StatusEntry()
        location = factories.Location(t_entry=entry)

        update_entry(
            entry_id=entry.id,
            status=entry.t_post.m_post_status,
            visibility=entry.t_post.visibility,
            title="",
            content=entry.e_content,
            syndication_urls=[],
            streams=[],
            location=None,
        )

        with pytest.raises(entry_models.TLocation.DoesNotExist):
            location.refresh_from_db()
