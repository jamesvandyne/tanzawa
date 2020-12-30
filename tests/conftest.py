import pytest


@pytest.fixture
def client():
    from rest_framework.test import APIClient
    return APIClient()
