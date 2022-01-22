import pytest


@pytest.mark.django_db
def test_favicon(client):
    response = client.get("/favicon.ico")

    assert response.status_code == 200
    assert response["Cache-Control"] == "max-age=86400, immutable, public"
    assert response["Content-Type"] == "image/svg+xml"
    assert response.content.startswith(b"<svg")
