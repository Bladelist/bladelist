# Generated by Django 3.2.4 on 2021-10-08 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_site', '0024_alter_bot_invite_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botmeta',
            name='prefix',
            field=models.CharField(blank=True, default='N/A', max_length=20, null=True),
        ),
    ]
