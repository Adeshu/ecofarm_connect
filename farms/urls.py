# corrected urls code inserted here
from django.urls import path
from . import views

app_name = 'farms'

urlpatterns = [
    path('', views.farm_list, name='farm_list'),
    path('create/', views.farm_create, name='farm_create'),
    path('<uuid:farm_id>/', views.farm_detail, name='farm_detail'),
    path('<uuid:farm_id>/edit/', views.farm_edit, name='farm_edit'),
    path('<uuid:farm_id>/crop/add/', views.crop_create, name='crop_create'),
    path('<uuid:farm_id>/crop/<int:crop_id>/edit/', views.crop_edit, name='crop_edit'),
    path('<uuid:farm_id>/activity/add/', views.activity_create, name='activity_create'),
    path('directory/', views.public_farms, name='public_farms'),
]
