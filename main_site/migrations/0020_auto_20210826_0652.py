# Generated by Django 3.2.4 on 2021-08-26 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0019_bot_admins'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botmeta',
            name='uptime',
        ),
        migrations.AddField(
            model_name='bot',
            name='uptime',
            field=models.FloatField(default=100, null=True),
        ),
    ]
