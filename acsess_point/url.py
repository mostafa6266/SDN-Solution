from django.contrib import admin
from django.urls import path 
from acsess_point import views


urlpatterns = [
   path('', views.access_points_view, name='access_points_view'),
    path('<int:pk>', views.acsess_data, name='access_point'),
    ] 

