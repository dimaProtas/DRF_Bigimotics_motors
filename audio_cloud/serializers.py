from rest_framework import serializers
from app.serializers import UsersSerializer
from . import models


class GenerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.GenerModel
        fields = '__all__'


class TrackSerializer(serializers.ModelSerializer):
    gener = GenerSerializer(read_only=True)
    user = UsersSerializer(read_only=True)
    class Meta:
        model = models.TrackModel
        fields = '__all__'


class LicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LicenceModel
        fields = '__all__'


class PlayListSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True, many=True)
    user = UsersSerializer(read_only=True)
    class Meta:
        model = models.PlayListModel
        fields = '__all__'
