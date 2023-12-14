from django.db import models
from pages.models import Building , Vlan
from cidrfield.models import IPNetworkField
from django.core.exceptions import ValidationError
from ipaddress import ip_network
# AccessPoint
class IpAdress(models.Model):
    ip_range = IPNetworkField(unique=True)
    building = models.OneToOneField(Building, on_delete=models.CASCADE, related_name='ip_address')

    def __str__(self):
        return f'{str(self.ip_range)} - {self.building}'

    def get_first_available_ip(self):
        network = ip_network(self.ip_range)
        used_ips = set(AccessPoint.objects.filter(
            building__ip_address=self).values_list('ip_address', flat=True))

        for ip in network.hosts():
            if str(ip) not in used_ips:
                return str(ip)

        raise ValidationError("No available IPs in the range")

class AccessPoint(models.Model):
    name = models.CharField(max_length=50)
    human_name = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(unique=True, null=True, blank=True)
    vendor = models.CharField(max_length=50, default='default_vendor_name')
    description = models.TextField(blank=True, null=True)
    vlan = models.ForeignKey(Vlan, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    wifi_password = models.CharField(max_length=50 )
    admin_user = models.CharField(max_length=50  )
    admin_password = models.CharField(max_length=50  )
    mac_address = models.CharField(max_length=25, unique=True)
    port_status = models.CharField(max_length=10 , default='enable')
    real_port = models.CharField(max_length=10 , null=True , blank=True)
    switch_ip = models.GenericIPAddressField(null=True , blank=True)




    def save(self, *args, **kwargs):
        if not self.ip_address:
            if self.building and hasattr(self.building, 'ip_address'):
                self.ip_address = self.building.ip_address.get_first_available_ip()
            else:
                raise ValidationError("Building must have an associated IP range.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.human_name} ({self.ip_address} - {self.id})"
    

    


