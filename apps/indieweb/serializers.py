from ninka.indieauth import discoverAuthEndpoints
from rest_framework import serializers

from . import constants


class MicropubSerializer(serializers.Serializer):
    h = serializers.CharField(required=True)
    access_token = serializers.CharField(required=False)
    action = serializers.CharField(required=False)
    url = serializers.URLField(required=False)

    def validate_h(self, value):
        v = value.lower()
        if v not in constants.supported_microformats:
            raise serializers.ValidationError(f" {value} is an unsupported h-type")
        return v


class CreateMicropubSerializer(MicropubSerializer):
    action = serializers.CharField(required=True)


ResponseTypeChoices = [("id", "id"), ("code", "id+authorization")]


class IndieAuthAuthorizationSerializer(serializers.Serializer):

    me = serializers.URLField(required=True)
    client_id = serializers.URLField(required=True)
    redirect_uri = serializers.URLField(required=True)
    state = serializers.CharField(required=True)
    scope = serializers.CharField(required=True)
    response_type = serializers.ChoiceField(choices=ResponseTypeChoices, required=False)

    def validate(self, data):
        if data["redirect_uri"]:
            response = discoverAuthEndpoints(data["client_id"])
            if data["redirect_uri"] not in response["redirect_uri"]:
                raise serializers.ValidationError(
                    "Redirect uri not found on client app"
                )

        return data
