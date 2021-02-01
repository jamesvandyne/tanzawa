# Generated by Django 3.1.4 on 2021-02-01 21:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0005_rename_published_updated_columns'),
        ('indieweb', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TWebmentionSend',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('target', models.URLField()),
                ('dt_sent', models.DateTimeField()),
                ('success', models.BooleanField()),
                ('t_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ref_t_webmention_send', to='post.tpost')),
            ],
            options={
                'db_table': 't_webmention_send',
                'unique_together': {('target', 't_post')},
            },
        ),
    ]