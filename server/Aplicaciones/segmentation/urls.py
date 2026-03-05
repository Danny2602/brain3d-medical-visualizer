from django.urls import include, path
from . import views

urlpatterns = [
    path('segmentacion/', views.ImageUploadView.as_view(), name='image-upload'),
]