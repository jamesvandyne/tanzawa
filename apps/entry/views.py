from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from post.models import MPostKind

from . import forms, models


@login_required
def status_create(request):
    form = forms.CreateStatusForm(request.POST or None, p_author=request.user)

    if request.method == "POST":
        if form.is_valid():
            form.prepare_data()
            entry = form.save()
            messages.success(request, "Saved Status")
            return redirect(resolve_url("status_edit", pk=entry.pk))
    context = {"form": form, "nav": "status"}
    return render(request, "entry/status_create.html", context=context)


@login_required
def status_edit(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related("t_post"), pk=pk)

    form = forms.UpdateStatusForm(request.POST or None, instance=status)

    if request.method == "POST":
        if form.is_valid():
            form.prepare_data()
            form.save()
            messages.success(request, "Saved Status")
    context = {"form": form, "nav": "status"}
    return render(request, "entry/status_update.html", context=context)


@login_required
def status_detail(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related("t_post"), pk=pk)
    context = {"status": status, "nav": "status"}
    return render(request, "entry/status_detail.html", context=context)


@login_required
def status_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects, pk=pk)
    status.delete()
    # TODO: Should we also delete the t_post ?
    messages.success(request, "Status Deleted")
    return redirect(resolve_url("status_list"))


@method_decorator(login_required, name="dispatch")
class TEntryListView(ListView):
    template_name = "entry/status_list.html"
    m_post_kind_key = None
    m_post_kind = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.m_post_kind_key:
            self.m_post_kind = get_object_or_404(MPostKind, key=self.m_post_kind_key)

    def get_queryset(self):
        qs = models.TEntry.objects.all()
        if self.m_post_kind:
            qs = qs.filter(t_post__m_post_kind=self.m_post_kind)
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["nav"] = "status"
        return context
