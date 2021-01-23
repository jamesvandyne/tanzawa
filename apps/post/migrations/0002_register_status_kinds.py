# Generated by Django 3.1.4 on 2020-12-30 22:49

from django.db import migrations


def register_default_post_statuses(apps, schema):

    MPostStatus = apps.get_model("post", "MPostStatus")

    MPostStatus.objects.get_or_create(key="published", name="Published")
    MPostStatus.objects.get_or_create(key="draft", name="Draft")


def register_default_post_kinds(apps, schema):

    MPostKind = apps.get_model("post", "MPostKind")

    MPostKind.objects.get_or_create(key="article", name="Article")
    MPostKind.objects.get_or_create(key="note", name="Note")
    MPostKind.objects.get_or_create(key="bookmark", name="Bookmark")
    MPostKind.objects.get_or_create(key="checkin", name="Checkin")
    MPostKind.objects.get_or_create(key="reply", name="Reply")
    MPostKind.objects.get_or_create(key="like", name="Like")


class Migration(migrations.Migration):

    dependencies = [
        ("post", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(register_default_post_statuses),
        migrations.RunPython(register_default_post_kinds),
    ]
