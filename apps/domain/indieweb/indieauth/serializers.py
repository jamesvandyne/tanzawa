from urllib.parse import urlparse

from data.indieweb.models import TToken
from ninka.indieauth import discoverAuthEndpoints
from rest_framework import serializers


class IndieAuthTokenSerializer(serializers.Serializer):
    me = serializers.URLField(required=False)
    client_id = serializers.URLField(write_only=True)
    redirect_uri = serializers.URLField(write_only=True)
    code = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)
    scope = serializers.CharField(read_only=True)

    def validate(self, data):
        if data["redirect_uri"]:
            if urlparse(data["redirect_uri"]).netloc != urlparse(data["client_id"]).netloc:
                response = discoverAuthEndpoints(data["client_id"])
                if data["redirect_uri"] not in response["redirect_uri"]:
                    raise serializers.ValidationError("Redirect uri not found on client app")
        try:
            t_token = TToken.objects.get(
                auth_token=data["code"], client_id=data["client_id"], exchanged_at__isnull=True
            )
        except TToken.DoesNotExist:
            raise serializers.ValidationError("Token not found")
        else:
            data["access_token"] = t_token.generate_key()
            data["t_token"] = t_token
            data["scope"] = " ".join(t_token.micropub_scope.values_list("key", flat=True))
        return data
