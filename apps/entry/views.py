from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from . import forms
from . import models


@login_required
def status_create(request):
    form = forms.CreateStatusForm(request.POST or None, p_author=request.user)

    if request.method == "POST":
        if form.is_valid():
            form.prepare_data()
            entry = form.save()
            messages.success(request, "Saved Status")
            return redirect(resolve_url("status_edit", pk=entry.pk))
    context = {
        'form': form
    }
    return render(request, "entry/status_create.html", context=context)


@login_required
def status_edit(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related('t_post'), pk=pk)

    form = forms.UpdateStatusForm(request.POST or None, instance=status)

    if request.method == "POST":
        if form.is_valid():
            form.prepare_data()
            form.save()
            messages.success(request, "Saved Status")
    context = {
        'form': form

    }
    return render(request, "entry/status_update.html", context=context)


@login_required
def status_detail(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related('t_post'), pk=pk)
    context = {
        'status': status

    }
    return render(request, "entry/status_detail.html", context=context)


@login_required
def status_delete(request, pk: int):
    status = get_object_or_404(models.TEntry.objects.select_related('t_post'), pk=pk)
    status.delete()
    messages.success(request, "Status Deleted")
    return redirect(resolve_url("status_list"))


@login_required
def status_list(request):
    objects = models.TEntry.objects.all()
    return render(request, "entry/status_list.html", context={"objects": objects})
