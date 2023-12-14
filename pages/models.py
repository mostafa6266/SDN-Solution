from django.db import models
from django.core.validators import RegexValidator
# Create your models here.


class Building(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return f"{self.name}"

class Switching (models.Model):
    name = models.CharField(max_length=50 , unique=True)
    ip_address = models.GenericIPAddressField(unique=True)
    vendor = models.CharField(max_length=50,default='default_vendor_name')
    website = models.URLField(blank=True, null=True )
    status = models.CharField(
    max_length=4,
    choices=(("UP", "UP"), ("DOWN", "DOWN")),
    default="DOWN",
    
)
    description = models.CharField(max_length=50,default='acsess' , null=True )
    mac_addresses_tables = models.TextField(blank=True, null=True)
    backup = models.TextField(blank=True, null=True)
    new_backup = models.TextField(blank=True, null=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.ip_address} - {self.name} - {self.building} - {self.id}"

class Vlan(models.Model):
    name = models.CharField(max_length=100,unique=True)
    # discrption = models.CharField(max_length=50 ,null=True , blank=True , default="none")

    def __str__(self):
        return f"{self.name} "
    
