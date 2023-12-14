"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from pages.views import homepage , switch , building_detail , custom_login , get_switches
from blocked_mac.views import Chek 
from mac_address.views import result 
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='home'),  # Define a URL pattern with the correct name
    path('search/', result, name='search_mac_address'),
    path('login/', custom_login, name="login"),
    path('switching/', switch, name="switch"),
    path('building/<int:building_id>/', building_detail, name='building_detail'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('blocked_mac_address/', Chek , name="blocked_mac_address"),
    path('get_switches/', get_switches, name='get_switches'),
    path('api/', include('monitor.url')),
    path('acsess_point/', include('acsess_point.url')),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL , document_root = settings.STATIC_ROOT)