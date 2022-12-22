from django.urls import reverse

from data.indieweb.models import TToken


class TokenNotFound(Exception):
    pass


class PermissionDenied(Exception):
    pass


def get_token_with_scope(*, key: str, action: str) -> TToken:
    try:
        t_token = TToken.objects.get(key__exact=key)
    except TToken.DoesNotExist:
        raise TokenNotFound()

    if not t_token.micropub_scope.filter(key__exact=action).exists():
        raise PermissionDenied(f"Token does not have {action} permissions.")
    return t_token


def get_user_for_token(*, key: str):
    return TToken.objects.select_related("user").get(key__exact=key).user


def get_new_token() -> str:
    return TToken.generate_key()


def get_me_url(*, request, t_token: TToken) -> str:
    return request.build_absolute_uri(reverse("public:author", args=[t_token.user.username]))
