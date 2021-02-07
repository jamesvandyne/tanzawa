from urllib.parse import urlparse

from django.db import transaction
from ninka.indieauth import discoverAuthEndpoints
from rest_framework import serializers

from . import constants
from .models import TToken


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
    response_type = serializers.ChoiceField(
        choices=ResponseTypeChoices, required=False, initial="id"
    )

    def validate(self, data):
        if data["redirect_uri"]:
            # Verify redirect uri if host name is different
            if (
                urlparse(data["redirect_uri"]).netloc
                != urlparse(data["client_id"]).netloc
            ):
                response = discoverAuthEndpoints(data["client_id"])
                if data["redirect_uri"] not in response["redirect_uri"]:
                    raise serializers.ValidationError(
                        "Redirect uri not found on client app"
                    )

        return data


class IndieAuthTokenSerializer(serializers.Serializer):
    me = serializers.URLField()
    client_id = serializers.URLField(write_only=True)
    redirect_uri = serializers.URLField(write_only=True)
    code = serializers.CharField(write_only=True)
    access_token = serializers.CharField(read_only=True)

    def validate(self, data):
        if data["redirect_uri"]:
            if (
                urlparse(data["redirect_uri"]).netloc
                != urlparse(data["client_id"]).netloc
            ):
                response = discoverAuthEndpoints(data["client_id"])
                if data["redirect_uri"] not in response["redirect_uri"]:
                    raise serializers.ValidationError(
                        "Redirect uri not found on client app"
                    )
        try:
            t_token = TToken.objects.get(
                auth_token=data["code"], client_id=data["client_id"]
            )
            data["access_token"] = t_token.generate_key()
            data["t_token"] = t_token

        except TToken.DoesNotExist:
            raise serializers.ValidationError("Token not found")
        return data

    @transaction.atomic
    def save(self, user):
        t_token = self.validated_data["t_token"]
        t_token.auth_token = ""
        t_token.access_token = self.validated_data["access_token"]
        t_token.save()
