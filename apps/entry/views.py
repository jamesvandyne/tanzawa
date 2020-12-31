from django.shortcuts import render

from . import forms
from . import models


def entry(request):
    form = forms.CreateArticleForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.prepare_data()
            entry = form.save()
            # todo: add some turoframe jazz

    context = {
        'form': form
    }
    return render(request, "entry/entry_create.html", context=context)


def entries(request):
    objects = models.TEntry.objects.all()
    return render(request, "entry/entry_list.html", context={"objects": objects})
