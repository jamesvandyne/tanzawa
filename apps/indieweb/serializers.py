from urllib.parse import urlparse

from django.db import transaction
from django.urls import reverse
from ninka.indieauth import discoverAuthEndpoints
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

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
    scope = serializers.CharField(read_only=True)

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
        except TToken.DoesNotExist:
            raise serializers.ValidationError("Token not found")
        else:
            data["access_token"] = t_token.generate_key()
            data["t_token"] = t_token
            data["scope"] = " ".join(
                t_token.micropub_scope.values_list("key", flat=True)
            )
        return data

    @transaction.atomic
    def save(self, user):
        t_token = self.validated_data["t_token"]
        t_token.auth_token = ""
        t_token.key = self.validated_data["access_token"]
        t_token.save()


class IndieAuthTokenVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)
    me = serializers.URLField(read_only=True)
    client_id = serializers.CharField(read_only=True)
    scope = serializers.CharField(read_only=True)

    def validate_token(self, value):
        try:
            return TToken.objects.get(key=value)
        except TToken.DoesNotExist:
            raise serializers.ValidationError("Token not found.")

    def validate(self, data):
        t_token = data['token']
        data["me"] = reverse("public:author", args=[t_token.user.username])
        data["client_id"] = t_token.client_id
        data["scope"] = " ".join(t_token.micropub_scope.values_list("key", flat=True))
        return data
