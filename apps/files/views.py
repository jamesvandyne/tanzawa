import mimetypes

from django.http import (FileResponse, HttpResponse, HttpResponseNotAllowed,
                         JsonResponse)
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import MediaUploadForm
from .models import TFile


@csrf_exempt
def micropub_media(request):
    """
    Micropub Media Endpoint
    """
    if request.method == "POST":
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            t_file = form.save()
            response = HttpResponse(status=201)
            response["Location"] = request.build_absolute_uri(t_file.get_absolute_url())
            return response
        return JsonResponse(
            status=400,
            data={"error": "invalid_request", "errors": form.errors.as_json()},
        )
    return HttpResponseNotAllowed(["POST"])


def get_media(request, uuid):
    t_file: TFile = get_object_or_404(TFile, uuid=uuid)
    mime_type, _ = mimetypes.guess_type(t_file.filename)
    response = FileResponse(t_file.file, mime_type, filename=t_file.filename)
    return response
