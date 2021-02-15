# Generated by Django 3.1.4 on 2021-02-15 20:44

from django.db import migrations


def add_default_streams(apps, schema_editor):
    MStream = apps.get_model("streams", "MStream")

    MStream.objects.create(icon="✏️", slug="articles", name="Articles")
    MStream.objects.create(icon="📤️", slug="replies", name="Replies")
    MStream.objects.create(icon="💬", slug="status", name="Status")
    MStream.objects.create(icon="🔖️️", slug="bookmarks", name="Bookmarks")
    MStream.objects.create(icon="🗺", slug="checkins", name="Checkins")
    MStream.objects.create(icon="📸", slug="photos", name="Photos")


class Migration(migrations.Migration):

    dependencies = [
        ("streams", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            add_default_streams, reverse_code=migrations.RunPython.noop
        ),
    ]
