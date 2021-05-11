from typing import Dict, Any
import logging
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
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
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header
from files.forms import MediaUploadForm


from .forms import IndieAuthAuthorizationForm
from .models import TWebmention
from .constants import MPostStatuses
from .location import location_to_pointfield_input
from .webmentions import send_webmention
from .utils import extract_base64_images, save_and_get_tag, render_attachment
from .serializers import (
    MicropubSerializer,
    IndieAuthAuthorizationSerializer,
    IndieAuthTokenSerializer,
    IndieAuthTokenVerificationSerializer,
    IndieAuthTokenRevokeSerializer,
)

logger = logging.getLogger(__name__)


def form_to_mf2(request):
    """ """
    properties = {}
    post = request.POST
    for key in post.keys():
        if key.endswith("[]"):
            key = key[:-2]
        if key == "access_token":
            continue
        properties[key] = post.getlist(key) + post.getlist(key + "[]")
    mf = {"type": [f'h-{post.get("h", "")}'], "properties": properties}
    return normalize_properties_to_underscore(mf)


def normalize_properties_to_underscore(data: Dict[str, Any]) -> Dict[str, Any]:
    """convert microformat2 property keys that use a hyphen to an underscore so DRF can serialize them"""
    properties = {}
    for key, value in data.get("properties", {}).items():
        properties[key.replace("-", "_")] = value
    return {"type": data["type"], "properties": properties}


def normalize_properties(data: Dict[str, Any]) -> Dict[str, Any]:
    h_entry = normalize_properties_to_underscore(data)
    return h_entry


@api_view(["GET", "POST"])
def micropub(request):
    normalize = {
        "application/json": lambda r: normalize_properties(r.data),
        "application/x-www-form-urlencoded": form_to_mf2,
        "multipart/form-data": form_to_mf2,
    }

    # authenticate
    auth = get_authorization_header(request)
    try:
        token = auth.split()[1].decode()
    except IndexError:
        token = request.POST.get("access_token")
    except UnicodeError:
        msg = _(
            "Invalid token header. Token string should not contain invalid characters."
        )
        return Response(data={"message": msg}, status=status.HTTP_400_BAD_REQUEST)

    if not token:
        msg = _("Invalid request. No credentials provided.")
        return Response(data={"message": msg}, status=status.HTTP_400_BAD_REQUEST)
    # normalize before sending to serializer
    try:
        body = normalize[request.content_type.split(";")[0]](request)
    except KeyError:
        return Response(
            data={"message": f"Invalid content-type: {request.content_type}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    props = body["properties"]
    if not body.get("access_token"):
        body["access_token"] = token
    body["type"] = body["type"][0]  # type is a list but needs to be a string
    if not body.get("action"):
        body["action"] = request.data.get("action", "create")

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
            props.get("post-status", [])
            or MPostStatuses.published  # pull this data from serialier
        ),
        "dt_published": dt_published[0].isoformat() if dt_published else None,
        "streams": serializer.validated_data["properties"]["streams"].values_list(
            "pk", flat=True
        ),
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
        named_forms["checkin"] = TCheckinModelForm(
            data=serializer.validated_data["properties"].get("checkin")
        )
    if serializer.validated_data["properties"].get("syndication"):
        for idx, syndication_url in enumerate(
            serializer.validated_data["properties"]["syndication"]
        ):
            named_forms[f"syndication_{idx}"] = TSyndicationModelForm(
                data={"url": syndication_url}
            )

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

    form = form_class(
        data=form_data, p_author=serializer.validated_data["access_token"].user
    )

    if form.is_valid() and all(
        named_form.is_valid() for named_form in named_forms.values()
    ):
        form.prepare_data()

        with transaction.atomic():
            entry = form.save()

            for named_form in named_forms.values():
                named_form.prepare_data(entry)
                named_form.save()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(request, entry.t_post, entry.e_content)

        response = Response(status=status.HTTP_201_CREATED)
        response["Location"] = request.build_absolute_uri(
            entry.t_post.get_absolute_url()
        )
        return response
    named_forms["entry"] = form
    response = {key: value.errors.as_json() for key, value in named_forms.items()}
    return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


@login_required
def review_webmention(request, pk: int, approval: bool):
    t_web_mention: TWebmention = get_object_or_404(
        TWebmention.objects.select_related(), pk=pk
    )
    t_webmention_response = t_web_mention.t_webmention_response

    with transaction.atomic():
        t_web_mention.approval_status = approval
        t_webmention_response.reviewed = True

        t_webmention_response.save()
        t_web_mention.save()
    # TODO: Once we have turbo enabled - add a ajax handler

    return redirect(reverse("post:dashboard"))


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
            redirect_uri = f"{form.cleaned_data['redirect_uri']}?code={t_token.auth_token}&state={form.cleaned_data['state']}"
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
            msg = _(
                "Invalid token header. Token string should not contain invalid characters."
            )
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
