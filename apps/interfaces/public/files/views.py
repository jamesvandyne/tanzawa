from data.files.constants import PICTURE_FORMATS
from data.files.models import TFile, TFormattedImage
from django.db.models import Q
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from domain.images.images import convert_image_format

from .forms import MediaUploadForm


@csrf_exempt
def micropub_media(request):
    """
    Micropub Media Endpoint
    """
    if not request.user.is_authenticated:
        return HttpResponseForbidden()

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
    return_file = t_file
    as_attachment = request.GET.get("content-disposition", "inline") == "attachment"
    file_format = request.GET.get("f")
    size = request.GET.get("s")

    if file_format in PICTURE_FORMATS.keys():
        qs = t_file.ref_t_formatted_image.filter(mime_type=file_format)
        if size:
            qs = qs.filter(Q(width=size) | Q(height=size))
        formatted_file = qs.first()
        if formatted_file:
            return_file = formatted_file
        else:
            upload_file, width, height = convert_image_format(
                t_file, target_mime=file_format, size=int(size) if size else None
            )
            if upload_file:
                formatted_file = TFormattedImage(
                    file=upload_file,
                    t_file=t_file,
                    mime_type=file_format,
                    filename=upload_file.name,
                    width=width,
                    height=height,
                )
                formatted_file.save()
                return_file = formatted_file
    elif size:
        qs = t_file.ref_t_formatted_image.filter(Q(width=size) | Q(height=size))
        formatted_file = qs.first()
        if formatted_file:
            return_file = formatted_file
        else:
            upload_file, width, height = convert_image_format(t_file, target_mime=t_file.mime_type, size=int(size))
            if upload_file:
                formatted_file = TFormattedImage(
                    file=upload_file,
                    t_file=t_file,
                    mime_type=t_file.mime_type,
                    filename=upload_file.name,
                    width=width,
                    height=height,
                )
                formatted_file.save()
                return_file = formatted_file
    # If there was an error creating a smaller version, the file has already been read so reset to 0.
    return_file.file.seek(0)
    response = FileResponse(
        return_file.file,
        return_file.mime_type,
        filename=return_file.filename,
        as_attachment=as_attachment,
    )
    return response
