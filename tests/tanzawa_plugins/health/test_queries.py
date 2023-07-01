import datetime

import freezegun

from tanzawa_plugin.health import queries


class TestGetDateFilter:
    @freezegun.freeze_time("2023-06-16", tick=False)
    def test_six_weeks(self):
        assert datetime.date(2023, 5, 5) == queries._get_six_weeks_ago()

    @freezegun.freeze_time("2023-06-16", tick=False)
    def test_first_of_month(self):
        assert datetime.date(2023, 6, 1) == queries._get_first_of_month()
