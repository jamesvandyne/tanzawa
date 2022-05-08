import logging

from application.indieweb import micropub as micropub_app
from application.indieweb import webmentions as webmention_app
from application.indieweb.location import location_to_pointfield_input
from bs4 import BeautifulSoup
from data.indieweb.constants import MPostStatuses
from django.db import transaction
from django.utils import timezone
from domain.indieweb import indieauth
from domain.indieweb.utils import (
    extract_base64_images,
    render_attachment,
    save_and_get_tag,
)
from domain.settings import queries as settings_queries
from interfaces.dashboard.entry.forms import (
    CreateArticleForm,
    CreateBookmarkForm,
    CreateCheckinForm,
    CreateReplyForm,
    CreateStatusForm,
    TCheckinModelForm,
    TLocationModelForm,
    TSyndicationModelForm,
)
from interfaces.public.files.forms import MediaUploadForm
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import (
    IndieAuthTokenSerializer,
    IndieAuthTokenVerificationSerializer,
    MicropubSerializer,
)

logger = logging.getLogger(__name__)


@api_view(["GET", "POST"])
def micropub(request):  # noqa: C901 too complex (30)
    """
    Micropub endpoint takes a micropub request, prepares images / data into the same
    structure as if they were posted via the web interface and uses those forms to process it.
    """

    # authenticate
    # TODO: Move indieauth into standard DRF/Django Middleware
    try:
        token = indieauth.authenticate_request(request=request)
    except indieauth.TokenNotFound:
        return Response(
            data={"message": "Invalid request. No credentials provided."}, status=status.HTTP_400_BAD_REQUEST
        )
    except indieauth.InvalidToken:
        return Response(data={"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    except indieauth.PermissionDenied:
        return Response(data={"message": "Scope permission denied"}, status=status.HTTP_400_BAD_REQUEST)

    # normalize before sending to serializer
    try:
        body = micropub_app.normalize_request(
            content_type=request.content_type,
            request_data=request.data,
            post_data=request.POST,
        )
    except micropub_app.UnknownContentType:
        return Response(
            data={"message": "Invalid content-type"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    else:
        props = body["properties"]

    # TODO: Layerize / refactor this view from here below. Will require layerizing entry app first.
    serializer = MicropubSerializer(data=body)
    if not serializer.is_valid():
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Save any photo attachments so we can append them to the content
    attachments = []
    for key in request.FILES:
        file_form = MediaUploadForm(files={"file": request.FILES[key]})
        if file_form.is_valid():
            t_file = file_form.save()
            attachments.append(t_file)
        else:
            return Response(
                data={"message": "Error uploading files"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Create entry form data
    named_forms = {}
    dt_published = serializer.validated_data["properties"].get("published", None)
    # Respect the active trip setting
    active_trip = settings_queries.get_active_trip()
    form_data = {
        "p_name": serializer.validated_data["properties"].get("name", ""),
        "e_content": serializer.validated_data["properties"].get("content", ""),
        "m_post_status": "".join(
            props.get("post-status", []) or MPostStatuses.published  # pull this data from serialier
        ),
        "dt_published": dt_published[0].isoformat() if dt_published else None,
        "streams": serializer.validated_data["properties"]["streams"].values_list("pk", flat=True),
        "visibility": serializer.validated_data["properties"]["visibility"].value,
        "t_trip": active_trip.id if active_trip else None,
    }
    if serializer.validated_data["properties"].get("in_reply_to"):
        linked_page = serializer.validated_data["properties"].get("in_reply_to")
        # adds u_in_reply_to, title, author, summary fields
        form_data.update(linked_page)
    elif serializer.validated_data["properties"].get("bookmark_of"):
        linked_page = serializer.validated_data["properties"].get("bookmark_of")
        # adds u_bookmark_of, title, author, summary fields
        form_data.update(linked_page)

    # Process related content
    if serializer.validated_data["properties"].get("location"):
        location = serializer.validated_data["properties"]["location"]
        location_form_data = {
            "street_address": location["location"].get("street_address", ""),
            "locality": location["location"].get("locality", ""),
            "region": location["location"].get("region", ""),
            "country_name": location["location"].get("country_name", ""),
            "postal_code": location["location"].get("postal_code", ""),
            "point": location_to_pointfield_input(location),
        }
        named_forms["location"] = TLocationModelForm(data=location_form_data)
    if serializer.validated_data["properties"].get("checkin"):
        named_forms["checkin"] = TCheckinModelForm(data=serializer.validated_data["properties"].get("checkin"))
    if serializer.validated_data["properties"].get("syndication"):
        for idx, syndication_url in enumerate(serializer.validated_data["properties"]["syndication"]):
            named_forms[f"syndication_{idx}"] = TSyndicationModelForm(data={"url": syndication_url})

    # Save and replace any embedded images
    soup = BeautifulSoup(form_data["e_content"], "html.parser")

    embedded_images = extract_base64_images(soup)
    photo_fields = serializer.validated_data["properties"].get("photo", [])
    for image in embedded_images + photo_fields:
        tag = save_and_get_tag(request, image)
        if not tag:
            continue
        # photo attachment
        if not image.tag:
            soup.append(tag)
            continue
        # Replace in e_content
        if image.tag.parent.name == "figure":
            image.tag.parent.replace_with(tag)
        else:
            image.tag.replace_with(tag)

    form_data["e_content"] = str(soup)

    # Append any attachments
    for attachment in attachments:
        tag = render_attachment(request, attachment)
        form_data["e_content"] += tag

    form_class = CreateStatusForm
    if form_data["p_name"]:
        form_class = CreateArticleForm
    if form_data.get("u_in_reply_to"):
        form_class = CreateReplyForm
    if form_data.get("u_bookmark_of"):
        form_class = CreateBookmarkForm
    if named_forms.get("checkin"):
        form_class = CreateCheckinForm

    form = form_class(data=form_data, p_author=indieauth.queries.get_user_for_token(key=token))

    if form.is_valid() and all(named_form.is_valid() for named_form in named_forms.values()):
        form.prepare_data()

        with transaction.atomic():
            entry = form.save()

            for named_form in named_forms.values():
                named_form.prepare_data(entry)
                named_form.save()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            webmention_app.send_webmention(request, entry.t_post, entry.e_content)

        response = Response(status=status.HTTP_201_CREATED)
        response["Location"] = request.build_absolute_uri(entry.t_post.get_absolute_url())
        return response
    named_forms["entry"] = form
    response = {key: value.errors.as_json() for key, value in named_forms.items()}
    return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST", "GET"])
def token_endpoint(request):
    if request.method == "GET":
        try:
            data = {"token": indieauth.extract_auth_token_from_request(request=request)}
        except indieauth.InvalidToken:
            return Response(
                data={"message": "Invalid token header. No credentials provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = IndieAuthTokenVerificationSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        if request.POST.get("action", "") == "revoke":
            indieauth.revoke_token(key=request.POST.get("token", ""))
            return Response(status=status.HTTP_200_OK)
        serializer = IndieAuthTokenSerializer(data=request.POST)
        if serializer.is_valid():
            # Exchange our auth_token for a new token
            t_token = serializer.validated_data["t_token"]
            with transaction.atomic():
                t_token.set_key(key=serializer.validated_data["access_token"])
                t_token.set_exchanged_at(exchanged_at=timezone.now())
            response_data = serializer.data
            response_data.update({"me": indieauth.queries.get_me_url(request=request, t_token=t_token)})
            return Response(data=response_data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
