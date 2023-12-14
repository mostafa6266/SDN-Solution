from rest_framework import serializers
from pages.models import Switching  # Import your model here

class SwitchesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Switching
        fields = ['name', 'ip_address', 'vendor', 'website', 'status', 'description', 
                  'mac_addresses_tables', 'backup', 'new_backup', 'building']
        extra_kwargs = {
            'website': {'required': False},
            'description': {'required': False, 'allow_null': True},
            'mac_addresses_tables': {'required': False, 'allow_null': True},
            'backup': {'required': False, 'allow_null': True},
            'new_backup': {'required': False, 'allow_null': True},
            # Add any other field-specific arguments here
        }
