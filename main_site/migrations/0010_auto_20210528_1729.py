# Generated by Django 3.2.3 on 2021-05-28 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0009_bot_banner_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botmeta',
            name='library',
            field=models.CharField(blank=True, default='N/A', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='botmeta',
            name='prefix',
            field=models.CharField(blank=True, default='N/A', max_length=10, null=True),
        ),
    ]