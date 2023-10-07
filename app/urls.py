from django.urls import path
from .views import UsersCustomViewSet


app_name = 'app'

urlpatterns = [
    path('', UsersCustomViewSet.as_view({'get': 'list'})),
]
