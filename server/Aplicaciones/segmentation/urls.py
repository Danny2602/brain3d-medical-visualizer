from django.urls import include, path
from . import views, views2

urlpatterns = [
    path('segmentacion/', views.ImageUploadView.as_view(), name='image-upload'),
    path('fourier/', views2.FourierUploadView.as_view(), name='fourier-upload'),
]