from django import forms
from .models import Switching

class SwitchForm(forms.ModelForm):
    class Meta:
        model = Switching
        fields = ['name', 'ip_address', 'vendor', 'website', 'description',  'building']
        widgets = {
            'vendor': forms.TextInput(attrs={'placeholder': 'e.g., cisco_ios_telnet, cisco_ios, hp_procurve'}),
            'description':forms.TextInput(attrs={'placeholder': 'e.g., acces , distribution , core'}),
        }