import logging
from typing import Optional

from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from post.models import TPost, MPostStatus, MPostKind
from entry.models import TEntry


from .serializers import CreateMicropubSerializer
from . import constants


logger = logging.getLogger(__name__)


def determine_post_kind(data) -> Optional[str]:
    try:
        post_kind = MPostKind.objects.get(key=data.get("post-kind"))
    except MPostStatus.DoesNotExist:
        post_kind = None
        logging.info(f"post-status: {data.get('post-kind')} doesn't exist")
    return post_kind or MPostKind.objects.get(key=constants.MPostKinds.article)


@api_view(["GET", "POST"])
def micropub(request):
    if request.method == 'GET':
        return Response(data={"hello": "world"})
    serializer = CreateMicropubSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # determine type
    if request.data.get("action") == "create":
        try:
            post_status = MPostStatus.objects.get(key=request.data.get("post-status"))
        except MPostStatus.DoesNotExist:
            logging.info(f"post-status: {request.data.get('post-status')} doesn't exist")
            return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        post_kind = determine_post_kind()
        if not post_kind:
            return Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        with transaction.atomic():
            post = TPost.objects.create(post_status=post_status, post_kind=post_kind)
            entry = TEntry(t_post=post_status, p_name=request.data.get('p-name'), e_content=request.data.get('e-content', ""))

    return Response(data=serializer.data)

