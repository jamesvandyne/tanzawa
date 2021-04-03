from pathlib import Path
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView
from django import forms
from django.http import Http404, HttpResponse, JsonResponse
from turbo_response import redirect_303, TurboFrame
from django.contrib import messages
from indieweb.utils import download_image
from files.images import bytes_as_upload_image
from files.forms import MediaUploadForm

from .models import TWordpress, TCategory, TPostKind, TWordpressAttachment
from .forms import WordpressUploadForm, TCategoryModelForm, TPostKindModelForm


@method_decorator(login_required, name="dispatch")
class TWordpressListView(ListView):

    model = TWordpress
    allow_empty = False

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect_303("wordpress:t_wordpress_create")


@method_decorator(login_required, name="dispatch")
class TWordpressCreate(CreateView):
    form_class = WordpressUploadForm
    template_name = "wordpress/wordpress_create.html"

    def get_success_url(self):
        return reverse("wordpress:tcategory_mapping", args=[self.object.pk])


@login_required
def category_mappings(request, pk):
    t_wordpress = get_object_or_404(TWordpress, pk=pk)
    TCategoryModelFormSet = forms.inlineformset_factory(
        TWordpress, TCategory, form=TCategoryModelForm, extra=0
    )
    formset = TCategoryModelFormSet(request.POST or None, instance=t_wordpress)
    if request.method == "POST" and formset.is_valid():
        formset.save()
        messages.success(request, "Updated Category Mapping")
        return redirect_303("wordpress:t_wordpress_list")
    context = {
        "t_wordpress": t_wordpress,
        "formset": formset,
    }
    return render(request, "wordpress/tcategory_mapping.html", context=context)


@login_required
def post_kind_mappings(request, pk):
    t_wordpress = get_object_or_404(TWordpress, pk=pk)
    TPostKindModelFormSet = forms.inlineformset_factory(
        TWordpress, TPostKind, form=TPostKindModelForm, extra=0
    )
    formset = TPostKindModelFormSet(request.POST or None, instance=t_wordpress)
    if request.method == "POST" and formset.is_valid():
        formset.save()
        messages.success(request, "Updated Post Kind Mapping")
        return redirect_303("wordpress:t_wordpress_list")
    context = {
        "t_wordpress": t_wordpress,
        "formset": formset,
    }
    return render(request, "wordpress/tpostkind_mapping.html", context=context)


@login_required
def t_wordpress_attachments(request, pk):
    t_wordpress = get_object_or_404(TWordpress, pk=pk)
    context = {
        "t_wordpress": t_wordpress,
        "attachment_count": t_wordpress.ref_t_wordpress_attachment.count(),
        "imported": t_wordpress.ref_t_wordpress_attachment.filter(
            t_file__isnull=False
        ).select_related("t_file"),
        "object_list": t_wordpress.ref_t_wordpress_attachment.filter(
            t_file__isnull=True
        ),
    }
    return render(request, "wordpress/twordpressattachment_list.html", context=context)


@login_required
def import_attachment(request, uuid):
    t_attachment = get_object_or_404(TWordpressAttachment, uuid=uuid)
    if t_attachment.t_file:
        return JsonResponse(status=400, data={"error": "already_imported"})
    data_image = download_image(t_attachment.guid)
    filename = Path(t_attachment.guid).name
    upload_image, _, _ = bytes_as_upload_image(
        data_image.image_data, data_image.mime_type, filename
    )
    form = MediaUploadForm(files={"file": upload_image})
    if form.is_valid():
        t_file = form.save()
        t_attachment.t_file = t_file
        t_attachment.save()
        response = HttpResponse(status=201)
        response["Location"] = request.build_absolute_uri(t_file.get_absolute_url())
    return (
        TurboFrame(uuid)
        .template(
            "wordpress/_attachment.html",
            context={
                "t_wordpress_attachment": t_attachment,
                "img_src": t_attachment.t_file.get_absolute_url(),
            },
        )
        .response(request)
    )


@login_required
def import_posts(request, pk):
    t_wordpress = get_object_or_404(TWordpress, pk=pk)
    context = {
        "t_wordpress": t_wordpress,
    }
    if request.method == "POST":
        pass

    return render(request, "wordpress/twordpressattachment_list.html", context=context)
