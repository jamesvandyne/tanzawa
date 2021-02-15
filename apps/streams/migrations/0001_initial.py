# Generated by Django 3.1.4 on 2021-02-15 20:41

import core.constants
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("post", "0005_rename_published_updated_columns"),
    ]

    operations = [
        migrations.CreateModel(
            name="MStream",
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
                ("icon", models.CharField(help_text="Select an emoji", max_length=1)),
                ("name", models.CharField(max_length=32)),
                ("slug", models.SlugField(unique=True)),
                (
                    "visibility",
                    models.SmallIntegerField(
                        choices=[
                            (core.constants.Visibility["PUBLIC"], "Public"),
                            (core.constants.Visibility["PRIVATE"], "Private"),
                            (core.constants.Visibility["UNLISTED"], "Unlisted"),
                        ],
                        default=core.constants.Visibility["PUBLIC"],
                    ),
                ),
            ],
            options={
                "db_table": "m_stream",
            },
        ),
        migrations.CreateModel(
            name="TStreamPost",
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
                    "m_stream",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="streams.mstream",
                    ),
                ),
                (
                    "t_post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="post.tpost"
                    ),
                ),
            ],
            options={
                "db_table": "t_stream_post",
                "unique_together": {("m_stream", "t_post")},
            },
        ),
        migrations.AddField(
            model_name="mstream",
            name="posts",
            field=models.ManyToManyField(
                through="streams.TStreamPost", to="post.TPost"
            ),
        ),
    ]
