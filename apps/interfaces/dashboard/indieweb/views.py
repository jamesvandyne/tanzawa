import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from rest_framework import status

from application.indieweb import webmentions as webmention_app
from data.indieweb.models import TWebmention
from domain.indieweb import indieauth
from domain.indieweb import webmention as webmention_domain

from .forms import IndieAuthAuthorizationForm
from .serializers import IndieAuthAuthorizationSerializer

logger = logging.getLogger(__name__)


@login_required
def review_webmention(request, pk: int, approval: bool):
    t_web_mention: TWebmention = get_object_or_404(TWebmention.objects.select_related(), pk=pk)

    webmention_app.moderate_webmention(t_web_mention=t_web_mention, approval=approval)

    webmentions = webmention_domain.pending_moderation()
    context = {
        "webmentions": webmentions,
        "unread_count": len(webmentions),
    }
    return TemplateResponse(request, "indieweb/fragments/webmentions.html", context)


@login_required
@require_GET
def _indieauth_authorize_form(request):
    serializer = IndieAuthAuthorizationSerializer(data=request.GET)

    if not serializer.is_valid():
        return HttpResponseBadRequest(serializer.errors.values())

    scopes = serializer.validated_data.get("scope", "").split(" ")
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


@csrf_exempt
def indieauth_authorize(request):
    """
    Implements the IndieAuth Authorization Request

    refs: https://indieauth.spec.indieweb.org/#authorization-request
    """
    if request.method == "GET":
        return _indieauth_authorize_form(request)
    elif request.method == "POST":
        serializer = indieauth.serializers.IndieAuthTokenSerializer(data=request.POST)
        if serializer.is_valid():
            t_token = serializer.validated_data["t_token"]
            with transaction.atomic():
                t_token.set_key(key=serializer.validated_data["access_token"])
                t_token.set_exchanged_at(exchanged_at=timezone.now())
            return JsonResponse(
                data={"me": indieauth.queries.get_me_url(request=request, t_token=t_token)},
                status=status.HTTP_200_OK,
            )
        return JsonResponse(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@login_required
@require_POST
def indieauth_authorize_request(request):
    """
    Save a request for authorization.
    """
    form = IndieAuthAuthorizationForm(request.POST)
    if form.is_valid():
        redirect_uri = f"{form.cleaned_data['redirect_uri']}?state={form.cleaned_data['state']}"
        t_token = indieauth.operations.create_token_for_user(
            user=request.user, client_id=form.cleaned_data["client_id"], scope=form.cleaned_data["scope"]
        )
        redirect_uri = f"{redirect_uri}&code={t_token.auth_token}"
        return redirect(redirect_uri)
    return redirect("indieauth_authorize")
