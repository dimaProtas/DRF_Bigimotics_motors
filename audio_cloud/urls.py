from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'track', views.TrackView)
router.register(r'playlist', views.PlayListView)
router.register(r'licence', views.LicenceView)


urlpatterns = [
    path('gener/', views.GenerView.as_view()),
    # path('track/', views.TrackView.as_view({'get': 'list'})),
    # path('licence/', views.LicenceView.as_view({'get': 'list'})),
    # path('playlist/', views.PlayListView.as_view({'get': 'list'})),
    path('', include(router.urls)),
]
