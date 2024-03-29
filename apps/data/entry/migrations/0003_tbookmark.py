# Generated by Django 3.1.4 on 2021-03-03 21:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("entry", "0002_treply"),
    ]

    operations = [
        migrations.CreateModel(
            name="TBookmark",
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
                ("u_bookmark_of", models.URLField()),
                ("title", models.CharField(blank=True, default="", max_length=128)),
                ("quote", models.TextField(blank=True, default="")),
                ("author", models.CharField(blank=True, default="", max_length=64)),
                ("author_url", models.URLField(blank=True, default="")),
                ("author_photo", models.URLField(blank=True, default="")),
                (
                    "t_entry",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="t_bookmark",
                        to="entry.tentry",
                    ),
                ),
            ],
            options={
                "db_table": "t_bookmark",
            },
        ),
    ]
