from rest_framework import authentication

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
