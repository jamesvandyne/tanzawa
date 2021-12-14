from indieweb import models


def get_webmention(*, webmention_id: int, t_post_id: int) -> models.TWebmention:
    return models.TWebmention.objects.get(t_webmention_response_id=webmention_id, t_post_id=t_post_id)


def pending_moderation():
    return (
        models.TWebmention.objects.filter(approval_status=None)
        .select_related("t_post", "t_webmention_response")
        .reverse()
    )
