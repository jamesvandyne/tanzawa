from typing import Dict, Optional
from urllib.parse import urlparse

from core.constants import Visibility
from django.core.validators import URLValidator
from django.db import transaction
from django.urls import reverse
from indieweb.application import extract
from indieweb.application import location as indieweb_location
from ninka.indieauth import discoverAuthEndpoints
from rest_framework import serializers
from streams.models import MStream

from . import constants
from .models import TToken
from .utils import DataImage, download_image


class ContentField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if isinstance(data, str):
            return data
        value = " \n".join(c if isinstance(c, str) else c["html"] for c in data)
        return value


class LocationField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if isinstance(data, list):
            if isinstance(data[0], str):
                # lat/long only form data
                location = indieweb_location.get_location({"properties": {"geo": data}})
            else:
                # already microformatted
                location = indieweb_location.get_location(data[0])
        else:
            location = indieweb_location.get_location(data)
        return location


class CheckinField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        if isinstance(data, list):
            return {
                "name": data[0].get("properties", {}).get("name", [""])[0],
                "url": data[0].get("properties", {}).get("url", [""])[0],
                "location": data[0].get("location"),
            }
        return data


class FlattenedStringField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data) -> str:
        if isinstance(data, str):
            return data
        value = "".join([v for v in data])
        return value


class VisibilityField(FlattenedStringField):
    """
    Converts micropub visibility to Tanzawa visibility IntEnum
    """

    def to_representation(self, value: Visibility):
        return value.to_micropub_property()

    def to_internal_value(self, data) -> Visibility:
        value = super().to_internal_value(data)
        return Visibility.from_micropub_property(value)


class PhotoField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data: str) -> DataImage:
        image = download_image(data)
        if not image:
            raise serializers.ValidationError("Unable to download photo at %s", data)
        return image


class EContentSerializer(serializers.Serializer):
    html = serializers.CharField(required=True)


class HEntryPropertiesSerializer(serializers.Serializer):

    name = FlattenedStringField(required=False)
    content = ContentField(required=False)
    category = serializers.ListSerializer(child=serializers.CharField(), required=False, write_only=True)
    photo = serializers.ListSerializer(child=PhotoField(required=False), required=False)
    streams = serializers.ModelSerializer(MStream.objects, read_only=True, required=False)
    published = serializers.ListSerializer(child=serializers.DateTimeField(), required=False)
    syndication = serializers.ListSerializer(child=serializers.URLField(), required=False)
    in_reply_to = FlattenedStringField(required=False, validators=[URLValidator])
    bookmark_of = FlattenedStringField(required=False, validators=[URLValidator])
    location = LocationField(required=False)
    checkin = CheckinField(required=False)
    visibility = VisibilityField(required=False, default=Visibility.PUBLIC)

    def _get_linked_page(self, url: str, url_key: str) -> Optional[Dict[str, str]]:
        linked_page = extract.extract_reply_details_from_url(url)
        link_dict = {
            url_key: url,
            "title": url,
            "author": "",
            "summary": "",
        }
        if linked_page:
            link_dict.update(
                {
                    url_key: linked_page.url,
                    "title": linked_page.title,
                    "author": linked_page.author.name if linked_page.author and linked_page.author.name else "",
                    "summary": linked_page.description,
                }
            )
        return link_dict

    def validate_in_reply_to(self, value: str) -> Optional[Dict[str, str]]:
        if value:
            return self._get_linked_page(value, "u_in_reply_to")
        return None

    def validate_bookmark_of(self, value: str) -> Optional[Dict[str, str]]:
        if value:
            return self._get_linked_page(value, "u_bookmark_of")
        return None

    def validate(self, data):
        if "category" in data:
            data["streams"] = MStream.objects.filter(slug__in=data["category"])
        else:
            data["streams"] = MStream.objects.none()
        return data


class MicropubSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    url = serializers.URLField(required=False)
    properties = HEntryPropertiesSerializer(required=True)

    def validate_type(self, value):
        v = value.lower()
        try:
            return constants.Microformats(v)
        except ValueError:
            raise serializers.ValidationError(f" {value} is an unsupported h-type")


class CreateMicropubSerializer(MicropubSerializer):
    action = serializers.CharField(required=True)


ResponseTypeChoices = [("id", "id"), ("code", "id+authorization")]


class IndieAuthAuthorizationSerializer(serializers.Serializer):

    me = serializers.URLField(required=True)
    client_id = serializers.URLField(required=True)
    redirect_uri = serializers.URLField(required=True)
    state = serializers.CharField(required=True)
    scope = serializers.CharField(required=True)
    response_type = serializers.ChoiceField(choices=ResponseTypeChoices, required=False, initial="id")

    def validate(self, data):
        if data["redirect_uri"]:
            # Verify redirect uri if host name is different
            if urlparse(data["redirect_uri"]).netloc != urlparse(data["client_id"]).netloc:
                response = discoverAuthEndpoints(data["client_id"])
                if data["redirect_uri"] not in response["redirect_uri"]:
                    raise serializers.ValidationError("Redirect uri not found on client app")

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
            if urlparse(data["redirect_uri"]).netloc != urlparse(data["client_id"]).netloc:
                response = discoverAuthEndpoints(data["client_id"])
                if data["redirect_uri"] not in response["redirect_uri"]:
                    raise serializers.ValidationError("Redirect uri not found on client app")
        try:
            t_token = TToken.objects.get(auth_token=data["code"], client_id=data["client_id"])
        except TToken.DoesNotExist:
            raise serializers.ValidationError("Token not found")
        else:
            data["access_token"] = t_token.generate_key()
            data["t_token"] = t_token
            data["scope"] = " ".join(t_token.micropub_scope.values_list("key", flat=True))
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
        t_token = data["token"]
        data["me"] = reverse("public:author", args=[t_token.user.username])
        data["client_id"] = t_token.client_id
        data["scope"] = " ".join(t_token.micropub_scope.values_list("key", flat=True))
        return data


class IndieAuthTokenRevokeSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate_token(self, value):
        try:
            return TToken.objects.get(key=value)
        except TToken.DoesNotExist:
            return None

    def save(self, user):
        t_token = self.validated_data["token"]
        if t_token:
            t_token.delete()
