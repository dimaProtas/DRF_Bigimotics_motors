from django.db import models
from django.core.validators import FileExtensionValidator
from app.models import UserAbstract
from audio_cloud.service import get_path_track_list_cover_album, get_path_upload_track_file, validate_size_img


class LicenceModel(models.Model):
    user = models.ForeignKey(UserAbstract, on_delete=models.CASCADE, related_name='licence')
    text = models.TextField(max_length=1000)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Лицензия'
        verbose_name_plural = 'Лицензии'


class GenerModel(models.Model):
    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class TrackModel(models.Model):
    user = models.ForeignKey(UserAbstract, on_delete=models.CASCADE, related_name='track')
    title = models.CharField(max_length=100)
    licence = models.ForeignKey(LicenceModel, on_delete=models.PROTECT, related_name='licence_track')
    gener = models.ManyToManyField(GenerModel, related_name='track_geners')
    file = models.FileField(
        upload_to=get_path_upload_track_file,
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav'])]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    plays_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    user_of_likes = models.ManyToManyField(UserAbstract, related_name='likes_of_tracks')

    def __str__(self):
        return f'{self.user} - {self.title}'

    class Meta:
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'


class PlayListModel(models.Model):
    user = models.ForeignKey(UserAbstract, on_delete=models.CASCADE, related_name='play_list')
    title = models.CharField(max_length=50)
    track = models.ManyToManyField(TrackModel, related_name='track_list')
    cover = models.ImageField(
        upload_to=get_path_track_list_cover_album,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg']), validate_size_img]
    )

    class Meta:
        verbose_name = 'Плейлист'
        verbose_name_plural = 'Плейлисты'


