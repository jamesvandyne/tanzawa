import json
import logging
from bs4 import BeautifulSoup
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from entry.models import TEntry
from entry.forms import CreateStatusForm
from post.models import MPostStatus, TPost
from post.utils import determine_post_kind
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header
from PIL import Image

from files.forms import MediaUploadForm
from files.images import bytes_as_upload_image

from .authentication import IndieAuthentication
from .forms import IndieAuthAuthorizationForm
from .models import TWebmention
from .constants import MPostKinds, MPostStatuses
from .webmentions import send_webmention
from .utils import extract_base64_images
from .serializers import (
    MicropubSerializer,
    IndieAuthAuthorizationSerializer,
    IndieAuthTokenSerializer,
    IndieAuthTokenVerificationSerializer,
    IndieAuthTokenRevokeSerializer,
)

logger = logging.getLogger(__name__)


def form_to_mf2(request):
    """"""
    properties = {}
    post = request.POST
    for key in post.keys():
        if key.endswith("[]"):
            key = key[:-2]
        if key == "access_token":
            continue
        properties[key] = post.getlist(key) + post.getlist(key + "[]")

    return {"type": [f'h-{post.get("h", "")}'], "properties": properties}


@api_view(["GET", "POST"])
def micropub(request):
    normalize = {
        "application/json": lambda r: r.data,
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
    body = normalize[request.content_type.split(";")[0]](request)
    props = body["properties"]
    if not body.get("access_token"):
        body["access_token"] = token
    body["type"] = body["type"][0]  # type is a list but needs to be a string
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

    # post_kind = MPostKinds.note
    # if serializer.data["h"] != "entry":
    #     post_kind = serializer.data["h"]
    #
    # if props.get("name"):
    #     post_kind = MPostKinds.article

    form_data = {
        "e_content": " \n".join(
            c if isinstance(c, str) else c["html"] for c in props.get("content", [])
        ),
        "m_post_status": "".join(
            props.get("post-status", []) or MPostStatuses.published
        ),
    }

    # save any encoded images
    soup = BeautifulSoup(form_data["e_content"], "html.parser")

    embedded_images = extract_base64_images(soup)
    for image in embedded_images:
        # convert base64 embeded image to a SimpleFileUpload object
        upload_file, width, height = bytes_as_upload_image(
            image.decode(), image.mime_type
        )
        if not upload_file:
            continue
        # Save to disk
        file_form = MediaUploadForm(files={"file": upload_file})
        if file_form.is_valid():
            t_file = file_form.save()
            img_src = request.build_absolute_uri(t_file.get_absolute_url())
            context = {
                "mime": image.mime_type,
                "src": img_src,
                "width": width,
                "height": height,
                "trix_attachment_data": json.dumps(
                    {
                        "contentType": image.mime_type,
                        "filename": upload_file.name,
                        "filesize": t_file.file.size,
                        "height": height,
                        "href": f"{img_src}?content-disposition=attachment",
                        "url": img_src,
                        "width": width,
                    }
                ),
            }
            # Render as trix
            tag = BeautifulSoup(render_to_string("trix/figure.html", context), 'html.parser')
            # Replace in e_content
            if image.tag.parent.name == "figure":
                image.tag.parent.replace_with(tag)
            else:
                image.tag.replace_with(tag)

    form_data["e_content"] = str(soup)

    for attachment in attachments:
        img = Image.open(attachment.file)
        img_src = request.build_absolute_uri(attachment.get_absolute_url())
        context = {
            "mime": attachment.mime_type,
            "src": img_src,
            "width": img.width,
            "height": img.height,
            "trix_attachment_data": json.dumps(
                {
                    "contentType": attachment.mime_type,
                    "filename": attachment.filename,
                    "filesize": attachment.file.size,
                    "height": img.height,
                    "href": f"{img_src}?content-disposition=attachment",
                    "url": img_src,
                    "width": img.width,
                }
            ),
        }
        tag = render_to_string("trix/figure.html", context)
        form_data["e_content"] += tag

    form = CreateStatusForm(
        data=form_data, p_author=serializer.validated_data["access_token"].user
    )
    if form.is_valid():
        form.prepare_data()
        entry = form.save()

        if form.cleaned_data["m_post_status"].key == MPostStatuses.published:
            send_webmention(request, entry.t_post, entry.e_content)

        response = Response(status=status.HTTP_201_CREATED)
        response["Location"] = request.build_absolute_uri(
            entry.t_post.get_absolute_url()
        )
        return response
    return Response(data=form.errors, status=status.HTTP_400_BAD_REQUEST)


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


@method_decorator(login_required, name="dispatch")
class TEntryListView(ListView):
    template_name = "entry/status_list.html"

    def get_queryset(self):
        qs = TWebmention.objects.all()
        if self.m_post_kind:
            qs = qs.filter(t_post__m_post_kind=self.m_post_kind)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["nav"] = "status"
        return context


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
