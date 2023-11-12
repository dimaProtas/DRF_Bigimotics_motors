from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework import viewsets, permissions
from . import models
from . import serializers


class GenerView(ListAPIView):
    queryset = models.GenerModel.objects.all()
    serializer_class = serializers.GenerSerializer
    permission_classes = [permissions.IsAuthenticated]


class TrackView(viewsets.ModelViewSet):
    queryset = models.TrackModel.objects.all()
    serializer_class = serializers.TrackSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = [permissions.IsAuthenticated]


class LicenceView(viewsets.ModelViewSet):
    queryset = models.LicenceModel.objects.all()
    serializer_class = serializers.LicenceSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = [permissions.IsAuthenticated]


class PlayListView(viewsets.ModelViewSet):
    queryset = models.PlayListModel.objects.all()
    serializer_class = serializers.PlayListSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = [permissions.IsAuthenticated]