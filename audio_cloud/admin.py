from django.contrib import admin
from .models import LicenceModel, PlayListModel, TrackModel, GenerModel


class LicenceAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'text']
    list_display_links = ['id']


@admin.register(PlayListModel)
class PlayListAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'cover']
    list_display_links = ['id']


@admin.register(TrackModel)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'licence', 'file', 'created_at', 'plays_count']
    list_display_links = ['id']


@admin.register(GenerModel)
class GenerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id']


admin.site.register(LicenceModel, LicenceAdmin)