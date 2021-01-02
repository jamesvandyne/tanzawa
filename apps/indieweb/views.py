import logging

from django.db import transaction
from entry.models import TEntry
from post.models import MPostStatus, TPost
from post.utils import determine_post_kind
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import CreateMicropubSerializer

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
