from decimal import Decimal

import pytest
from django.urls import reverse

from tanzawa_plugin.health import constants, models


@pytest.mark.django_db
class TestHealth:
    def test_can_record_health(self, client, factory):
        admin = factory.User()
        payload = {
            "weight": Decimal("75.12"),
            "weight_unit": constants.WeightUnitChoices.KILOGRAMS,
            "mood": constants.MoodChoices.POSITIVE,
        }

        # Login as a user ...
        client.force_login(admin)

        # ... and submit our health form
        response = client.post(reverse("plugin_health_admin:add_daily_health"), payload)

        # It should be a success
        assert response.status_code == 302

        # With a single Weight record...
        assert models.Weight.objects.count() == 1
        weight = models.Weight.objects.first()
        assert weight.measurement == Decimal("75.12")
        assert weight.unit == constants.WeightUnitChoices.KILOGRAMS

        # ... and a single mood record
        assert models.Mood.objects.count() == 1
        mood = models.Mood.objects.first()
        assert mood.measurement == constants.MoodChoices.POSITIVE
