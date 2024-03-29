# Generated by Django 3.2.2 on 2021-06-03 10:12

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wordpress", "0004_fk_set_null"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tcategory",
            options={"verbose_name": "Wordpress Category", "verbose_name_plural": "Wordpress Categories"},
        ),
        migrations.AlterModelOptions(
            name="tpostformat",
            options={"verbose_name": "Wordpress Post Format", "verbose_name_plural": "Wordpress Post Formats"},
        ),
        migrations.AlterModelOptions(
            name="tpostkind",
            options={"verbose_name": "Wordpress Post Kind", "verbose_name_plural": "Wordpress Post Kinds"},
        ),
        migrations.AlterModelOptions(
            name="twordpress",
            options={"verbose_name": "Wordpress", "verbose_name_plural": "Wordpress"},
        ),
        migrations.AlterModelOptions(
            name="twordpressattachment",
            options={"verbose_name": "Wordpress Attachment", "verbose_name_plural": "Wordpress Attachments"},
        ),
        migrations.AlterModelOptions(
            name="twordpresspost",
            options={"verbose_name": "Wordpress Post", "verbose_name_plural": "Wordpress Posts"},
        ),
    ]
