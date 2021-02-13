# Generated by Django 3.1.4 on 2021-02-06 21:18

from django.db import migrations


def register_micropub_scopes(apps, schema):

    MMicropubScope = apps.get_model("indieweb", "MMicropubScope")

    MMicropubScope.objects.get_or_create(key="create", name="Create")
    MMicropubScope.objects.get_or_create(key="update", name="Update")
    MMicropubScope.objects.get_or_create(key="delete", name="Delete")
    MMicropubScope.objects.get_or_create(key="draft", name="Draft")
    MMicropubScope.objects.get_or_create(key="media", name="Media")


class Migration(migrations.Migration):

    dependencies = [
        ("indieweb", "0003_ttoken"),
    ]

    operations = [
        migrations.RunPython(
            register_micropub_scopes, reverse_code=migrations.RunPython.noop
        )
    ]
