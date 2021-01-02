from django.shortcuts import render
from django.contrib import messages

from . import forms
from . import models


def status_create(request):
    form = forms.CreateArticleForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.prepare_data()
            entry = form.save()
            # todo: add some turoframe jazz
            form = forms.CreateArticleForm()
            messages.success(request, "Saved Status")

    context = {
        'form': form
    }
    return render(request, "entry/status_create.html", context=context)


def status_list(request):
    objects = models.TEntry.objects.all()
    return render(request, "entry/status_list.html", context={"objects": objects})
