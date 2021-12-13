import logging

from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from entry.forms import (
    CreateArticleForm,
    CreateBookmarkForm,
    CreateCheckinForm,
    CreateReplyForm,
    CreateStatusForm,
    TCheckinModelForm,
    TLocationModelForm,
    TSyndicationModelForm,
)
from files.forms import MediaUploadForm
from indieweb.application import micropub as micropub_app
from indieweb.application import webmentions as webmention_app
from indieweb.application.location import location_to_pointfield_input
from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import api_view
from rest_framework.response import Response
from turbo_response import TurboFrame

from .constants import MPostStatuses
from .domain import indieauth as authentication_domain
from .domain import webmention as webmention_domain
from .forms import IndieAuthAuthorizationForm
from .models import TWebmention
from .serializers import (
    IndieAuthAuthorizationSerializer,
    IndieAuthTokenRevokeSerializer,
    IndieAuthTokenSerializer,
    IndieAuthTokenVerificationSerializer,
    MicropubSerializer,
)
from .utils import extract_base64_images, render_attachment, save_and_get_tag

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
        token = authentication_domain.authenticate_request(request=request)
    except authentication_domain.TokenNotFound:
        return Response(
            data={"message": "Invalid request. No credentials provided."}, status=status.HTTP_400_BAD_REQUEST
        )
    except authentication_domain.InvalidToken:
        return Response(data={"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
    except authentication_domain.PermissionDenied:
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
    form_data = {
        "p_name": serializer.validated_data["properties"].get("name", ""),
        "e_content": serializer.validated_data["properties"].get("content", ""),
        "m_post_status": "".join(
            props.get("post-status", []) or MPostStatuses.published  # pull this data from serialier
        ),
        "dt_published": dt_published[0].isoformat() if dt_published else None,
        "streams": serializer.validated_data["properties"]["streams"].values_list("pk", flat=True),
        "visibility": serializer.validated_data["properties"]["visibility"].value,
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

    form = form_class(data=form_data, p_author=authentication_domain.queries.get_user_for_token(key=token))

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


@login_required
def review_webmention(request, pk: int, approval: bool):
    t_web_mention: TWebmention = get_object_or_404(TWebmention.objects.select_related(), pk=pk)

    webmention_app.moderate_webmention(t_web_mention=t_web_mention, approval=approval)

    webmentions = webmention_domain.pending_moderation()
    context = {
        "webmentions": webmentions,
        "unread_count": len(webmentions),
    }
    return TurboFrame("webmentions").template("indieweb/fragments/webmentions.html", context).response(request)


@login_required
def indieauth_authorize(request):

    if request.method == "GET":
        serializer = IndieAuthAuthorizationSerializer(data=request.GET)

        if not serializer.is_valid():
            return HttpResponseBadRequest(serializer.errors.values())

        scopes = serializer.validated_data["scope"].split(" ")
        form = IndieAuthAuthorizationForm(
            initial={
                "scope": scopes,
                "redirect_uri": serializer.validated_data["redirect_uri"],
                "client_id": serializer.validated_data["client_id"],
                "state": serializer.validated_data["state"],
            }
        )
        context = {
            "form": form,
            "client_id": serializer.validated_data.get("client_id"),
        }
        return render(request, "indieweb/indieauth/authorization.html", context=context)

    if request.method == "POST":
        form = IndieAuthAuthorizationForm(request.POST)
        if form.is_valid():
            t_token = form.save(request.user)
            redirect_uri = (
                f"{form.cleaned_data['redirect_uri']}?code={t_token.auth_token}&state={form.cleaned_data['state']}"
            )
            return redirect(redirect_uri)
        context = {"form": form, "client_id": form.cleaned_data["client_id"]}

        return render(request, "indieweb/indieauth/authorization.html", context=context)


@api_view(["POST", "GET"])
def token_endpoint(request):
    if request.method == "GET":
        auth = get_authorization_header(request)
        try:
            token = auth.split()[1]
        except IndexError:
            msg = _("Invalid token header. No credentials provided.")
            return Response(data={"message": msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = {"token": token.decode()}
        except UnicodeError:
            msg = _("Invalid token header. Token string should not contain invalid characters.")
            return Response(data={"message": msg}, status=status.HTTP_400_BAD_REQUEST)

        serializer = IndieAuthTokenVerificationSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        if request.POST.get("action", "") == "revoke":
            serializer = IndieAuthTokenRevokeSerializer(data=request.POST)
        else:
            serializer = IndieAuthTokenSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save(request.user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
