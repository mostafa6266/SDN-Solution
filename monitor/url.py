from django.contrib import admin
from django.urls import path 
from monitor import views


urlpatterns = [
   path('', views.creat),
   path("list/" ,views.test_api ),
   path('<int:pk>' , views.switch)
    ] 

