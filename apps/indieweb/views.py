import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from entry.models import TEntry
from post.models import MPostStatus, TPost
from post.utils import determine_post_kind
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import IndieAuthAuthorizationForm
from .models import TWebmention
from .serializers import CreateMicropubSerializer, IndieAuthAuthorizationSerializer

logger = logging.getLogger(__name__)


@api_view(["GET", "POST"])
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
        form = None
        if serializer.is_valid():
            scopes = serializer.validated_data['scope'].split(",")
            form = IndieAuthAuthorizationForm(initial={'scope': [scopes]})
        context = {
            "form": form,
            "client_id": serializer.validated_data.get("client_id"),


        }
        return render(request, "indieweb/indieauth/authorization.html", context=context)
