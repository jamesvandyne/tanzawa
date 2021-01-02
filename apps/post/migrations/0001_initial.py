# Generated by Django 3.1.4 on 2020-12-30 22:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MPostKind",
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
                ("key", models.CharField(max_length=16, unique=True)),
                ("name", models.CharField(max_length=16)),
            ],
            options={
                "db_table": "m_post_kind",
            },
        ),
        migrations.CreateModel(
            name="MPostStatus",
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
                ("key", models.CharField(max_length=16, unique=True)),
                ("name", models.CharField(max_length=16)),
            ],
            options={
                "db_table": "m_post_status",
            },
        ),
        migrations.CreateModel(
            name="TPost",
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
                ("published", models.DateTimeField(blank=True, null=True)),
                ("updated", models.DateTimeField(blank=True, null=True)),
                (
                    "m_post_kind",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="post.mpostkind"
                    ),
                ),
                (
                    "m_post_status",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="post.mpoststatus",
                    ),
                ),
                (
                    "p_author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="auth.user"
                    ),
                ),
            ],
            options={
                "db_table": "t_post",
            },
        ),
    ]