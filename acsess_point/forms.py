from django import forms
from django.core.exceptions import ValidationError
import re
from .models import AccessPoint
from pages.models import Building, Vlan

class AccessPointForm(forms.ModelForm):
    building = forms.ModelChoiceField(queryset=Building.objects.all(), empty_label="Select a Building")
    vlan = forms.ModelChoiceField(queryset=Vlan.objects.all(), empty_label="Select a VLAN")
    mac_address = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={'pattern': '^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$'}),
        error_messages={'invalid': 'Enter a valid MAC address.'}
    )

    class Meta:
        model = AccessPoint
        fields = ['name', 'human_name', 'vendor', 'description', 'mac_address', 'wifi_password', 'admin_user', 'admin_password', 'vlan', 'building']

    def clean_mac_address(self):
        mac_address = self.cleaned_data.get('mac_address')
        if not re.match('^([0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}$', mac_address):
            raise ValidationError('Enter a valid MAC address.')
        return mac_address
