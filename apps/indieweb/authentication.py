from rest_framework.authentication import TokenAuthentication
from .models import TToken


class IndieAuthentication(TokenAuthentication):
    model = TToken
    keyword = "Bearer"
