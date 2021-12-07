from .. import models


def get_webmention(*, webmention_id: int, t_post_id: int) -> models.TWebmention:
    return models.TWebmention.objects.get(t_webmention_response_id=webmention_id, t_post_id=t_post_id)
