import functools

from domain.sunbottle import client as sunbottle_client


@functools.lru_cache(maxsize=2)
def get_generation(hour: int):
    """
    Get the total generation from the configured Sunbottle instance.
    """
    client = sunbottle_client.get_client()
    try:
        return client.get_generation()
    except sunbottle_client.SunbottleClientError:
        return {}
