from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.image_upload, name='image_upload'),
    path('upload/success/', views.image_upload_success, name='image_upload_success'),
    path('search/', views.image_search, name='image_search'),
]