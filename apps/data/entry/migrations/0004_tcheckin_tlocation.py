# Generated by Django 3.1.4 on 2021-03-07 21:54

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("entry", "0003_tbookmark"),
    ]

    operations = [
        migrations.CreateModel(
            name="TLocation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "street_address",
                    models.CharField(blank=True, default="", max_length=128),
                ),
                ("locality", models.CharField(blank=True, default="", max_length=128)),
                ("region", models.CharField(blank=True, default="", max_length=64)),
                (
                    "country_name",
                    models.CharField(blank=True, default="", max_length=64),
                ),
                (
                    "postal_code",
                    models.CharField(blank=True, default="", max_length=16),
                ),
                (
                    "point",
                    django.contrib.gis.db.models.fields.PointField(geography=True, srid=3857),
                ),
                (
                    "t_entry",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="t_location",
                        to="entry.tentry",
                    ),
                ),
            ],
            options={
                "db_table": "t_location",
            },
        ),
        migrations.CreateModel(
            name="TCheckin",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("url", models.URLField(blank=True, null=True)),
                (
                    "t_entry",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="t_checkin",
                        to="entry.tentry",
                    ),
                ),
                (
                    "t_location",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="t_checkin",
                        to="entry.tlocation",
                    ),
                ),
            ],
            options={
                "db_table": "t_checkin",
            },
        ),
    ]
