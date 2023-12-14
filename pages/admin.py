from django.contrib import admin
from .models import Switching,Building,Vlan 
# Register your models here.
admin.site.register(Building)
admin.site.register(Switching)
admin.site.register(Vlan)
