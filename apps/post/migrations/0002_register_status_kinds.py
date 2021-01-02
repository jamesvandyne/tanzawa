# Generated by Django 3.1.4 on 2020-12-30 22:49

from django.db import migrations


def register_default_post_statuses(apps, schema):

    MPostStatus = apps.get_model("post", "MPostStatus")

    MPostStatus.objects.get_or_create(key="published", name="Published")
    MPostStatus.objects.get_or_create(key="draft", name="Draft")


def register_default_post_kinds(apps, schema):

    MPostKind = apps.get_model("post", "MPostKind")

    MPostKind.objects.get_or_create(key="article")
    MPostKind.objects.get_or_create(key="note")
    MPostKind.objects.get_or_create(key="bookmark")
    MPostKind.objects.get_or_create(key="checkin")
    MPostKind.objects.get_or_create(key="reply")
    MPostKind.objects.get_or_create(key="like")


class Migration(migrations.Migration):

    dependencies = [
        ("post", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(register_default_post_statuses),
        migrations.RunPython(register_default_post_kinds),
    ]