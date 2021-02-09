import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from entry.models import TEntry
from post.models import MPostStatus, TPost
from post.utils import determine_post_kind
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header

from .authentication import IndieAuthentication
from .forms import IndieAuthAuthorizationForm
from .models import TWebmention
from .serializers import (
    CreateMicropubSerializer,
    IndieAuthAuthorizationSerializer,
    IndieAuthTokenSerializer,
    IndieAuthTokenVerificationSerializer,
    IndieAuthTokenRevokeSerializer,
)

logger = logging.getLogger(__name__)


@api_view(["GET", "POST"])
@authentication_classes([IndieAuthentication])
def micropub(request):
    if request.method == "GET":
        return Response(data={"hello": "world"})
    serializer = CreateMicropubSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # determine type
    if request.data.get("action") == "create":
        try:
            post_status = MPostStatus.objects.get(key=request.data.get("post-status"))
        except MPostStatus.DoesNotExist:
            logging.info(
                f"post-status: {request.data.get('post-status')} doesn't exist"
            )
            return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        post_kind = determine_post_kind(request.data)
        if not post_kind:
            return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with transaction.atomic():
            post = TPost.objects.create(
                m_post_status=post_status, m_post_kind=post_kind
            )
            entry = TEntry.objects.create(
                t_post=post,
                p_name=request.data.get("p-name", ""),
                e_content=request.data.get("e-content", ""),
            )

    return Response(data=serializer.data)


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
