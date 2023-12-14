from django.conf import settings
from mac_address.models import Git_mac_address_table
from monitor.models import RunMonitoring


def schedule ():
    Git_mac_address_table()

def monitor():
    RunMonitoring()