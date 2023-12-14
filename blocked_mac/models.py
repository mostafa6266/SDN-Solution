from django.db import models
from netmiko import ConnectHandler
from datetime import datetime
import re
from pages.models import Switching
from django.utils.timezone import now
# Create your models here.

class Blocked_Mac_Address(models.Model):
    switch_ip =  models.GenericIPAddressField(unique=False,default="core ip")
    mac_address = models.CharField(max_length=25 )
    vlan = models.CharField(max_length=25)
    reason = models.CharField(max_length=100,default="None" , null=True)
    created_at = models.DateTimeField(default=datetime.now , blank=True )
    def __str__(self):
        return f"{self.mac_address} - {self.switch_ip} - vlan {self.vlan} " 






def check_mac_from_core():
    device = {
        'device_type': 'hp_comware',
        'ip': "core ip",
        'username': "user",
        'password': "password",
    }

    try:
        connection = ConnectHandler(**device)

        connection.disable_paging()

        output = connection.send_command("display mac-address blackhole")

        pattern = r"([0-9a-fA-F-]+)\s+(\d+)\s+Blackhole"
        matches = re.findall(pattern, output)
        def format_mac(formatted_mac):
            reversed_mac = formatted_mac.replace("-", "")
            reversed_mac = '-'.join([reversed_mac[i:i+2] for i in range(0, len(reversed_mac), 2)])
            return reversed_mac
        

        for match in matches:
            mac = match[0]
            vlan = int(match[1])
    
            formatted_mac = format_mac(mac)



            if not Blocked_Mac_Address.objects.filter(mac_address=formatted_mac, vlan=vlan).exists() :
                # If it doesn't exist, add it to the database
                blocked_mac = Blocked_Mac_Address(mac_address=formatted_mac, vlan=vlan, reason="Blackhole")
                blocked_mac.save()
            else:
                pass
        connection.disconnect()
    except Exception as e:
        return "cant conect the core"




def convert_mac_format(mac_address):
    # Remove all hyphens
    mac_address = mac_address.replace("-", "")
    
    # Insert hyphens after every 4 characters
    new_mac_address = '-'.join(mac_address[i:i+4] for i in range(0, 12, 4))
    
    return new_mac_address



def get_device_type(ip_address):
            try:
                switch = Switching.objects.get(ip_address=ip_address)
                return switch.vendor
            except Switching.DoesNotExist:
                return None


def block_from_core(mac , vlan ):
    device = {
        'device_type': 'hp_comware',
        'ip': "core ip",
        'username': "user",
        'password': "password",
    }

    try:
        connection = ConnectHandler(**device)
        mac1 = convert_mac_format(mac)
        connection.disable_paging()
        connection.send_command("system-view",expect_string="[HP]")
        output = connection.send_command(f"mac-address blackhole {mac1} vlan {vlan}")
    except:
        return None
    


def undo_block_from_core(mac , vlan ):
    device = {
        'device_type': 'hp_comware',
        'ip': "core ip",
        'username': "user",
        'password': "password",
        
    }


    connection = ConnectHandler(**device)
    mac1 = convert_mac_format(mac)
    connection.disable_paging()
    connection.send_command("system-view",expect_string="[HP]")
    output = connection.send_command(f"undo mac-address blackhole {mac1} vlan {vlan}")
    connection.disconnect()
    





def check_mac_from_all(vendor , ipaddress):
    device = {
        'device_type': vendor,
        'ip': ipaddress,
        'username': "user",
        'password': "password",
    }
    connection = ConnectHandler(**device)
    if vendor == "cisco_ios" or vendor == "cisco_ios_telnet":
        
        def convert_mac_format_for_cisco(mac_address):
            # Remove the periods
            mac = mac_address.replace('.', '')
            return '-'.join(mac[i:i+2] for i in range(0, len(mac), 2))
        output = connection.send_command("show mac address-table")
        for line in output.split('\n'):
            if 'Drop' in line:
                parts = line.split()
                if len(parts) >= 4:
                        # Extract VLAN, MAC address, and reason
                        vlan, mac_address, _, reason = parts[:4]
                        mac_address_f = convert_mac_format_for_cisco(mac_address)   
                if not Blocked_Mac_Address.objects.filter(mac_address=mac_address_f, vlan=vlan).exists() :        
                    Blocked_Mac_Address.objects.create(
                            switch_ip=ipaddress,
                            mac_address=mac_address_f,
                            vlan=vlan,
                            reason=reason,
                            created_at=now()
                        )  
        connection.disconnect()
              

    elif vendor == "hp_procurve":
        pass


def get_device_type(ip_address):
    try:
        switch = Switching.objects.get(ip_address=ip_address)
        return switch.vendor
    except Switching.DoesNotExist:
        return None


def blocke_in_switch(mac , ipaddress , vlan):
    vendor = get_device_type(ipaddress)
    device = {
        'device_type': vendor,
        'ip': ipaddress ,
        'username': "user",
        'password': "password",
        'secret':"password",
    }
    
    connection = ConnectHandler(**device)
    connection.enable()
    connection.config_mode()
    connection.send_config_set(f"mac address-table static {mac} vlan {vlan} drop ")
    connection.save_config()
    
# mac address-table static 3408.0499.981c  vlan X drop


def undo_blocke_in_switch(mac , vlan , ipaddress ):
    vendor = get_device_type(ipaddress)
    device = {
        'device_type': vendor,
        'ip': ipaddress ,
        'username': "user",
        'password': "password",
        'secret':"password",
    }
    
    connection = ConnectHandler(**device)
    connection.enable()
    connection.send_config_set(f"no mac address-table static {mac} vlan {vlan} drop ")
    connection.save_config()


# mac address-table static 20f3.a357.fee8 vlan x drop
class Blocke_from_switch:
    def __init__(self, switch_ip, mac, vlan) -> None:
        self.switch = Switching.objects.filter(ip_address=switch_ip).first()
        self.device = {
            'device_type': self.switch.vendor,
            'host': self.switch.ip_address,
            'username': 'user',
            'password': 'password',
            'secret': 'password',
        }
        self.mac = mac
        self.vlan = vlan

        if self.switch.vendor in ["cisco_ios", "cisco_ios_telnet"]:
            self.cisco()

        elif self.switch.vendor == "hp_procurve":  
            self.hp()  
            
        else:
            return None
    def cisco(self):
        try:
            with ConnectHandler(**self.device) as connection:
                connection.enable()
                output = connection.send_config_set(f"mac address-table static {self.mac} vlan {self.vlan} drop ")
                connection.save_config()
        except:
            return None
        
    def hp(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                output = net_connect.send_config_set(f'lockout-mac {self.mac}')
                net_connect.disconnect()
        except:
            return None    

class Undo_Blocke_from_switch:
    def __init__(self, switch_ip, mac, vlan) -> None:
        self.switch = Switching.objects.filter(ip_address=switch_ip).first()
        self.device = {
            'device_type': self.switch.vendor,
            'host': self.switch.ip_address,
            'username': 'user',
            'password': 'password',
            'secret': 'password',
        }
        self.mac = mac
        self.vlan = vlan

        if self.switch.vendor in ["cisco_ios", "cisco_ios_telnet"]:
            self.cisco()

        elif self.switch.vendor == "hp_procurve":  
            self.hp()  
            
        else:
            return None
    def cisco(self):
        try:
            with ConnectHandler(**self.device) as connection:
                connection.enable()
                output = connection.send_config_set(f"no mac address-table static {self.mac} vlan {self.vlan} drop ")
                connection.save_config()
        except:
            return None
        
    def hp(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                output = net_connect.send_config_set(f'no lockout-mac {self.mac}')
                net_connect.disconnect()
        except:
            return None    
        

class Change_vlan:
    def __init__(self, switch_ip, port, vlan) -> None:
        self.switch = Switching.objects.filter(ip_address=switch_ip).first()
        self.device = {
            'device_type': self.switch.vendor,
            'host': self.switch.ip_address,
            'username': 'user',
            'password': 'password',
            'secret': 'password',
        }
        self.port = port
        self.vlan = vlan

        if self.switch.vendor in ["cisco_ios", "cisco_ios_telnet"]:
            self.cisco()

        elif self.switch.vendor == "hp_procurve":  
            self.hp()  
            
        else:
            return None

    def cisco(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                config_commands = [f'interface {self.port}', f'switchport access vlan {self.vlan} ' , 'sh' , 'no sh']
                output = net_connect.send_config_set(config_commands)
                net_connect.disconnect() 
        except:
            return None

    def hp(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                config_commands = [f'vlan {self.vlan}', f'untagged {self.port}' , f'interface {self.port}' , 'disable' , 'enable' ]
                output = net_connect.send_config_set(config_commands)
                net_connect.disconnect()
        except:
            return None





class Display_vlan:
    def __init__(self, switch_ip, port,) -> None:
        self.switch = Switching.objects.filter(ip_address=switch_ip).first()
        
        self.device = {
            'device_type': self.switch.vendor,
            'host': self.switch.ip_address,
            'username': 'user',
            'password': 'password',
            'secret': 'password',
        }
        self.port = port
        

        if self.switch.vendor in ["cisco_ios", "cisco_ios_telnet"]:
            self.output = self.cisco() 
        elif self.switch.vendor == "hp_procurve":  
            self.output = self.hp()  

        else:
            return None
        
    
    def cisco(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                command = f'show mac address-table interface {self.port}'  # Command as a string
                output = net_connect.send_command(command)  # Send a single command string
                net_connect.disconnect()
                return output
        except Exception as e:
            return None

    def hp(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                config_commands = f'show mac-address {self.port}'
                output = net_connect.send_command(config_commands)
                net_connect.disconnect()
                return output
        except:
            return None



class ShutdownPort:
    def __init__(self, switch_ip, port) -> None:
        self.switch = Switching.objects.filter(ip_address=switch_ip).first()
        # Check if switch is None
        if not self.switch:
            raise ValueError(f"Switch with IP {switch_ip} not found")
        self.device = {
            'device_type': self.switch.vendor,
            'host': self.switch.ip_address,
            'username': 'user',
            'password': 'password',
            'secret': 'password',
        }
        self.port = port

        if self.switch.vendor in ["cisco_ios", "cisco_ios_telnet"]:
            self.cisco()

        elif self.switch.vendor == "hp_procurve":  
            self.hp()  
            
        else:
            return None
    def cisco(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                config_commands = [f'interface {self.port}','sh']
                output = net_connect.send_config_set(config_commands)
                net_connect.disconnect() 
        except:
            return None

    def hp(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                config_commands = [f'interface {self.port}' , 'disable' ]
                output = net_connect.send_config_set(config_commands)
                net_connect.disconnect()
        except:
            return None
class NoShutdownPort:
    def __init__(self, switch_ip, port) -> None:
        self.switch = Switching.objects.filter(ip_address=switch_ip).first()
        if not self.switch:
            raise ValueError(f"Switch with IP {switch_ip} not found")
        self.device = {
            'device_type': self.switch.vendor,
            'host': self.switch.ip_address,
            'username': 'user',
            'password': 'password',
            'secret': 'password',
        }
        self.port = port

        if self.switch.vendor in ["cisco_ios", "cisco_ios_telnet"]:
            self.cisco()

        elif self.switch.vendor == "hp_procurve":  
            self.hp()  
            
        else:
            return None
    def cisco(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                config_commands = [f'interface {self.port}','no sh']
                output = net_connect.send_config_set(config_commands)
                net_connect.disconnect() 
        except:
            return None

    def hp(self):
        try:
            with ConnectHandler(**self.device) as net_connect:
                net_connect.enable()
                config_commands = [f'interface {self.port}' , 'enable' ]
                output = net_connect.send_config_set(config_commands)
                net_connect.disconnect()
        except:
            return None
