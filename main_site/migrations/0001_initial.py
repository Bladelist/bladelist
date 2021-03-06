# Generated by Django 3.2.3 on 2021-05-31 18:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('invite_link', models.URLField()),
                ('votes', models.IntegerField(default=0)),
                ('verification_status', models.CharField(choices=[('VERIFIED', 'Verified'), ('UNVERIFIED', 'Unverified'), ('REJECTED', 'Rejected')], default='UNVERIFIED', max_length=20)),
                ('online', models.BooleanField(default=False)),
                ('banned', models.BooleanField(default=False)),
                ('verified', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField()),
                ('server_count', models.IntegerField(default=0)),
                ('avatar', models.CharField(max_length=100, null=True)),
                ('short_desc', models.CharField(max_length=120, null=True)),
                ('banner_url', models.URLField(default='https://i.postimg.cc/15TN17rQ/xirprofilback.jpg')),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('tag', models.CharField(default='0000', max_length=4)),
                ('avatar', models.CharField(max_length=100, null=True)),
                ('banned', models.BooleanField(default=False)),
                ('ban_reason', models.TextField(blank=True, null=True)),
                ('dm_channel', models.BigIntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('name', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('icon', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('creation_time', models.DateTimeField(null=True)),
                ('bot', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='all_votes', to='main_site.bot')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voted_bots', to='main_site.member')),
            ],
        ),
        migrations.CreateModel(
            name='MemberMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True)),
                ('twitter', models.URLField(blank=True, null=True)),
                ('github', models.URLField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('discordbio', models.URLField(blank=True, null=True)),
                ('facebook', models.URLField(blank=True, null=True)),
                ('reddit', models.URLField(blank=True, null=True)),
                ('member', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='meta', to='main_site.member')),
            ],
        ),
        migrations.CreateModel(
            name='BotReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('creation_date', models.DateTimeField()),
                ('reviewed', models.BooleanField(default=False)),
                ('bot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='main_site.bot')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported_bots', to='main_site.member')),
            ],
        ),
        migrations.CreateModel(
            name='BotMeta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uptime', models.FloatField(default=100)),
                ('prefix', models.CharField(blank=True, default='N/A', max_length=10, null=True)),
                ('github', models.URLField(blank=True, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('privacy', models.URLField(blank=True, null=True)),
                ('twitter', models.URLField(blank=True, null=True)),
                ('donate', models.URLField(blank=True, null=True)),
                ('support_server', models.URLField(blank=True, null=True)),
                ('library', models.CharField(blank=True, default='N/A', max_length=15, null=True)),
                ('ban_reason', models.TextField(blank=True, null=True)),
                ('shard_count', models.IntegerField(default=0, null=True)),
                ('rejection_count', models.IntegerField(default=0)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('long_desc', models.TextField(blank=True, null=True)),
                ('bot', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='meta', to='main_site.bot')),
                ('moderator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main_site.member')),
            ],
        ),
        migrations.AddField(
            model_name='bot',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bots', to='main_site.member'),
        ),
        migrations.AddField(
            model_name='bot',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='bots', to='main_site.Tag'),
        ),
    ]
