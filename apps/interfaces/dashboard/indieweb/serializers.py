from urllib.parse import urlparse

from ninka.indieauth import discoverAuthEndpoints
from rest_framework import serializers

ResponseTypeChoices = [("id", "id"), ("code", "id+authorization")]


class IndieAuthAuthorizationSerializer(serializers.Serializer):

    me = serializers.URLField(required=False)
    client_id = serializers.URLField(required=True)
    redirect_uri = serializers.URLField(required=True)
    state = serializers.CharField(required=True)
    scope = serializers.CharField(required=False)
    response_type = serializers.ChoiceField(choices=ResponseTypeChoices, required=False, initial="id")

    def validate(self, data):
        if data["redirect_uri"]:
            # Verify redirect uri if host name is different
            if urlparse(data["redirect_uri"]).netloc != urlparse(data["client_id"]).netloc:
                response = discoverAuthEndpoints(data["client_id"])
                if data["redirect_uri"] not in response["redirect_uri"]:
                    raise serializers.ValidationError("Redirect uri not found on client app")

        return data
