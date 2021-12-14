import logging
from pathlib import Path

from bs4 import BeautifulSoup
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import linebreaks_filter, safe
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView
from entry.forms import (
    CreateArticleForm,
    CreateBookmarkForm,
    CreateCheckinForm,
    CreateReplyForm,
    CreateStatusForm,
    TCheckinModelForm,
    TLocationModelForm,
    TSyndicationModelForm,
    UpdateArticleForm,
    UpdateBookmarkForm,
    UpdateCheckinForm,
    UpdateReplyForm,
    UpdateStatusForm,
)
from entry.models import TCheckin, TLocation
from files.forms import MediaUploadForm
from files.images import bytes_as_upload_image
from indieweb.application.location import location_to_pointfield_input
from indieweb.utils import download_image, render_attachment
from turbo_response import TurboFrame, redirect_303

from . import extract
from .forms import TCategoryModelForm, TPostKindModelForm, WordpressUploadForm
from .models import (
    TCategory,
    TPostKind,
    TWordpress,
    TWordpressAttachment,
    TWordpressPost,
)

logger = logging.getLogger(__name__)


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
        return reverse("wordpress:t_category_mapping", args=[self.object.pk])


@login_required
def category_mappings(request, pk):
    t_wordpress = get_object_or_404(TWordpress, pk=pk)
    TCategoryModelFormSet = forms.inlineformset_factory(TWordpress, TCategory, form=TCategoryModelForm, extra=0)
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
    TPostKindModelFormSet = forms.inlineformset_factory(TWordpress, TPostKind, form=TPostKindModelForm, extra=0)
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
        "imported": t_wordpress.ref_t_wordpress_attachment.filter(t_file__isnull=False).select_related("t_file"),
        "object_list": t_wordpress.ref_t_wordpress_attachment.filter(t_file__isnull=True),
    }
    return render(request, "wordpress/twordpressattachment_list.html", context=context)


@login_required
def import_attachment(request, uuid):
    t_attachment = get_object_or_404(TWordpressAttachment, uuid=uuid)
    if t_attachment.t_file:
        return JsonResponse(status=400, data={"error": "already_imported"})
    data_image = download_image(t_attachment.guid)
    filename = Path(t_attachment.guid).name
    upload_image, _, _ = bytes_as_upload_image(data_image.image_data, data_image.mime_type, filename)
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
        "unimported_attachments": t_wordpress.ref_t_wordpress_attachment.filter(t_file__isnull=True).exists(),
        "category_map": t_wordpress.ref_t_category.filter(m_stream__isnull=False).exists(),
        "postkind_map": t_wordpress.ref_t_post_kind.filter(m_post_kind__isnull=False).exists(),
    }
    if request.method == "POST":
        soup = BeautifulSoup(t_wordpress.export_file.read(), "xml")

        for t_post in t_wordpress.ref_t_wordpress_post.all():
            import_post(request, t_post, soup)
        messages.success(request, "Imported Posts 🎉")
    return render(request, "wordpress/import_posts.html", context=context)


def import_post(request, t_wordpress_post: TWordpressPost, soup: BeautifulSoup):  # noqa: C901  too complex (32)!

    guid = soup.find("guid", text=t_wordpress_post.guid)
    t_post = t_wordpress_post.t_post
    if t_post:
        t_entry = t_post.ref_t_entry
    else:
        t_entry = None

    if not guid:

        raise forms.ValidationError("Guid doesn't exist in export file")
    item = guid.parent
    logging.info("Processing %s", guid)
    named_forms = {}
    dt_published = extract.extract_published_date(item)
    categories = extract.extract_categories(item)
    form_data = {
        "p_name": item.find("title").text,
        "e_content": item.find("encoded").text,
        "m_post_status": "".join(extract.extract_post_status(item)),
        "dt_published": dt_published.isoformat() if dt_published else None,
        "streams": TCategory.objects.exclude(m_stream__isnull=True)
        .filter(nice_name__in=[nice_name for _, nice_name in categories])
        .values_list("m_stream_id", flat=True),
    }

    reply = extract.extract_in_reply_to(item)
    bookmark_of = extract.extract_bookmark(item)
    if reply:
        logging.info("Has reply")
        form_data.update(
            {
                "u_in_reply_to": reply.url,
                "title": reply.title,
                "author": reply.author.name if reply.author else "",
                "summary": reply.description,
            }
        )
    elif bookmark_of:
        logging.info("Has bookmark")
        form_data.update(
            {
                "u_bookmark_of": bookmark_of.url,
                "title": bookmark_of.title or bookmark_of.url,
                "author": bookmark_of.author.name if bookmark_of.author else "",
                "summary": bookmark_of.description,
            }
        )

    # Process related content
    location = extract.extract_location(item)
    checkin = extract.extract_checkin(item)
    syndication = extract.extract_syndication(item)
    if location:
        logging.info("Has location")
        location["point"] = location_to_pointfield_input(location["point"])
        try:
            t_location = t_entry.t_location
        except (TLocation.DoesNotExist, AttributeError):
            t_location = None

        named_forms["location"] = TLocationModelForm(data=location, instance=t_location)
    if checkin:
        logging.info("Has checkin")
        try:
            t_checkin = t_entry.t_checkin
        except (TCheckin.DoesNotExist, AttributeError):
            t_checkin = None
        named_forms["checkin"] = TCheckinModelForm(data=checkin, instance=t_checkin)
    if syndication:
        logging.info("Has syndication")
        for idx, syndication_url in enumerate(syndication):
            t_syndication = t_entry.t_syndication.filter(url=syndication_url).first() if t_entry else None
            named_forms[f"syndication_{idx}"] = TSyndicationModelForm(
                data={"url": syndication_url}, instance=t_syndication
            )

    # Rewrite any image links
    content = BeautifulSoup(form_data["e_content"], "html.parser")
    images = extract.extract_images(content, t_wordpress_post.t_wordpress.base_site_url)
    for image in images:
        image_url = image["src"].replace("-scaled", "").replace("https://micro.blog/photos/200/", "")
        image_attachment = (
            TWordpressAttachment.objects.filter(
                t_wordpress_id=t_wordpress_post.t_wordpress_id,
                guid__startswith=image_url,
            )
            .select_related("t_file")
            .first()
        )
        if image_attachment:
            tag = BeautifulSoup(render_attachment(request, image_attachment.t_file), "html.parser")
            if image.parent and image.parent.name == "a":
                image.parent.replace_with(tag)
            else:
                image.replace_with(tag)
        else:
            logger.info(
                "%s has no attachment is possibly a dead url t_wordpress_post.uuid=%s",
                image_url,
                t_wordpress_post.uuid,
            )
    form_data["e_content"] = str(content)

    # Append any attachments
    if t_wordpress_post.path != "/":
        for attachment in TWordpressAttachment.objects.filter(link__contains=t_wordpress_post.path):
            if attachment.t_file:

                if str(attachment.t_file.uuid) in form_data["e_content"]:
                    # File was already inserted into the post in the image rewrite step above. Skip.
                    continue

                if attachment.t_file.mime_type.startswith("video"):
                    form_data["e_content"].replace(
                        attachment.guid,
                        request.build_absolute_uri(attachment.t_file.get_absolute_url()),
                    )
                else:
                    tag = render_attachment(request, attachment.t_file)
                    form_data["e_content"] += tag

    form_data["e_content"] = linebreaks_filter(safe(form_data["e_content"]))

    if t_wordpress_post.t_post:
        form_class = UpdateStatusForm
        form_kwargs = {"instance": t_wordpress_post.t_post.ref_t_entry}
        if form_data["p_name"]:
            form_class = UpdateArticleForm
        if form_data.get("u_in_reply_to"):
            form_class = UpdateReplyForm
        if form_data.get("u_bookmark_of"):
            form_class = UpdateBookmarkForm
        if named_forms.get("checkin"):
            form_class = UpdateCheckinForm
    else:
        form_kwargs = {"p_author": request.user}
        form_class = CreateStatusForm
        if form_data["p_name"]:
            form_class = CreateArticleForm
        if form_data.get("u_in_reply_to"):
            form_class = CreateReplyForm
        if form_data.get("u_bookmark_of"):
            form_class = CreateBookmarkForm
        if named_forms.get("checkin"):
            form_class = CreateCheckinForm

    form = form_class(data=form_data, **form_kwargs)

    if form.is_valid() and all(named_form.is_valid() for named_form in named_forms.values()):
        form.prepare_data()
        with transaction.atomic():
            entry = form.save()

            for named_form in named_forms.values():
                named_form.prepare_data(entry)
                named_form.save()

            t_wordpress_post.t_post = entry.t_post
            t_wordpress_post.save()
    else:
        logger.error(form.errors)
