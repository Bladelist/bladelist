# Generated by Django 3.2.3 on 2021-05-29 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0012_botmeta_support_server'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='dm_channel',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]