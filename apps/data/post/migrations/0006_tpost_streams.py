# Generated by Django 3.1.4 on 2021-02-15 20:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("streams", "0001_initial"),
        ("post", "0005_rename_published_updated_columns"),
    ]

    operations = [
        migrations.AddField(
            model_name="tpost",
            name="streams",
            field=models.ManyToManyField(through="streams.TStreamPost", to="streams.MStream"),
        ),
    ]
