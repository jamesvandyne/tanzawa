from collections.abc import Iterable

from django.db import transaction
from rest_framework import authentication

from data.indieweb import models

from . import queries


class InvalidToken(Exception):
    pass


class TokenNotFound(Exception):
    pass


class PermissionDenied(Exception):
    pass


def authenticate_request(*, request) -> str:
    token_key = _extract_token_from_request(request)
    try:
        queries.get_token_with_scope(key=token_key, action=request.data.get("action", "create"))
    except queries.PermissionDenied:
        raise PermissionDenied()
    except queries.TokenNotFound:
        raise TokenNotFound()
    return token_key


def extract_auth_token_from_request(request) -> str:
    token = _extract_token_from_request(request)
    if not token:
        raise InvalidToken("Invalid token header. No credentials provided.")
    return token


@transaction.atomic
def create_token_for_user(*, user, client_id: str, scope: Iterable[models.MMicropubScope]) -> models.TToken:

    t_token = models.TToken.new(
        user=user,
        auth_token=queries.get_new_token(),
        client_id=client_id,
    )
    t_token.micropub_scope.set(scope)
    return t_token


def revoke_token(*, key: str) -> None:
    models.TToken.objects.filter(key__exact=key).delete()


def _extract_token_from_request(request) -> str:
    """Looks for an auth token in the http headers or in the form body"""
    auth = authentication.get_authorization_header(request)
    try:
        token = auth.split()[1].decode()
    except IndexError:
        token = request.POST.get("access_token")
    except UnicodeError:
        raise InvalidToken("Invalid token header.")

    return token
