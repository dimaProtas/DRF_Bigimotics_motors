# Generated by Django 4.2.4 on 2023-11-09 17:24

import audio_cloud.service
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GenerModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='LicenceModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=1000)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licence', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TrackModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to=audio_cloud.service.get_path_upload_track_file, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp3', 'wav'])])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('plays_count', models.PositiveIntegerField(default=0)),
                ('like_count', models.PositiveIntegerField(default=0)),
                ('gener', models.ManyToManyField(related_name='track_geners', to='audio_cloud.genermodel')),
                ('licence', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='licence_track', to='audio_cloud.licencemodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='track', to=settings.AUTH_USER_MODEL)),
                ('user_of_likes', models.ManyToManyField(related_name='likes_of_tracks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlayListModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('cover', models.ImageField(blank=True, null=True, upload_to=audio_cloud.service.get_path_track_list_cover_album, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg']), audio_cloud.service.validate_size_img])),
                ('track', models.ManyToManyField(related_name='track_list', to='audio_cloud.trackmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='play_list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
