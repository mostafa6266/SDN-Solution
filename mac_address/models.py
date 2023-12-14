from django.db import models
from netmiko import ConnectHandler ,  NetmikoTimeoutException, NetmikoAuthenticationException
from concurrent.futures import ThreadPoolExecutor, as_completed
from pages.models import Switching, Building 
import threading
import winrm
import re

class Search(models.Model):
    def search_mac_address(device_ip,mac_address):
        def get_device_type(ip_address):
            try:
                switch = Switching.objects.get(ip_address=ip_address)
                return switch.vendor
            except Switching.DoesNotExist:
                return None


        def extreme (device_ip,mac_address):
            device = {
            'device_type': 'extreme',
            'ip': device_ip,
            'username': "user",
            'password': "password",
            }

            mac_to_find_with_colons = mac_address 

            mac_to_find_with_hyphens = mac_to_find_with_colons.replace("-", ":")

            net_connect = ConnectHandler(**device)

            output = net_connect.send_command('show fdb')

            output_lines = output.split('\n')

            port = None

            mac_address = None
            vlan = None

            for line in output_lines:
                mac_match = re.search(r'^\s*([\da-fA-F:]+)\s+.*', line)
                if mac_match:
                    mac_address = mac_match.group(1)
                    if mac_address == mac_to_find_with_hyphens:
                        vlan_match = re.search(r'VLAN_([\d]+)', line)
                        if vlan_match:
                            vlan = vlan_match.group(1)
                        break
            if port is not None:
                output2 = net_connect.send_command('show ports vlan | include None')
                if port in output2:
                    return None
                else:
                    result = []
                    result.append(port)
                    result.append(vlan)
                    result.append(device_ip)
                    net_connect.disconnect()  
                    return result

        def is_trunk_port(device_ip, port):
            try:
                # Connect to the HP switch
                device = {
                    'device_type': 'hp_procurve',
                    'ip': device_ip,
                    'username': "user",
                    'password': "password",
                }
                connection = ConnectHandler(**device)

                # Run the command to get the running configuration
                output = connection.send_command("show run")

                # Function to check if a port is in a given range or list
                def is_port_in_list_or_range(port_list, port):
                    port = int(port)
                    for p in port_list.split(','):
                        if '-' in p:
                            start, end = map(int, p.split('-'))
                            if start <= port <= end:
                                return True
                        elif int(p) == port:
                            return True
                    return False

                # Parse the configuration to check for tagged status of the port
                is_trunk = False
                for line in output.splitlines():
                    # Skip irrelevant lines
                    if not line.strip().startswith('vlan') and not line.strip().startswith('tagged'):
                        continue

                    # Check for tagged status in VLANs other than VLAN 1
                    if 'tagged' in line and 'vlan 1' not in line:
                        tagged_ports = line.split('tagged')[-1].strip()
                        if is_port_in_list_or_range(tagged_ports, port):
                            is_trunk = True
                            break

                connection.disconnect()
                return is_trunk
            except Exception as e:
                return False

        
        try:
            # Determine the device type based on the IP address
            device_type = get_device_type(device_ip)
            # Connect to the device
            
            device = {
                'device_type': device_type,
                'ip': device_ip,
                'username': "user",
                'password': "password",
                'secret': "password",
            }
            connection = ConnectHandler(**device)
            connection.enable()
            resurlt = 0
            if "hp" in device_type:
                
                output = connection.send_command(f"show mac-address {mac_address}")
                
                
                mac_match = re.search(r'(\d+)\s+(\d+)', output)
                if mac_match:
                    port = mac_match.group(1)
                    vlan = mac_match.group(2)

                    if is_trunk_port(device_ip,port):
                        pass
                    else:   
                        result = []
                        result.append(mac_address) 
                        result.append(port)
                        result.append(vlan)
                        result.append(device_ip)
                        connection.disconnect()
                        return result
                else:
                    pass
            
            elif 'extreme' in device_type:
                result= extreme(device_ip,mac_address)
                if result:
                    return result
                else:
                    pass

            
            else:
                output = connection.send_command(f"show mac address-table address {mac_address}")
                port_match = re.search(r'(\S+\d+/\d+)', output)
                vlan_match = re.search(r'(\d+)', output)
                vlan = None
                if port_match:
                    port = port_match.group()
                    port_status = connection.send_command(f"show running-config interface {port}")
                    is_trunk = "trunk" in port_status
                if vlan_match:
                    vlan = vlan_match.group(1) 
                    if is_trunk:
                        pass
                    else:
                        result = []
                        result.append(mac_address) 
                        result.append(port)
                        result.append(vlan)
                        result.append(device_ip)
                        connection.disconnect()
                        return result
                        
                else:
                    pass

            connection.disconnect()
        except:
            pass    
    
        
   


stop_event = threading.Event()


class Return_result:
    def __init__(self, mac):
        global stop_event
        stop_event.clear()
        self.mac = mac
        methods = [getattr(Hospital_buildings, func) for func in dir(Hospital_buildings)
                   if callable(getattr(Hospital_buildings, func)) and not func.startswith("__")]

        self.result = None
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(method, self.mac) for method in methods]

            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    self.result = result
                    # Once a result is found, no need to wait for other futures
                    break

        self.other_values = [None] * (len(methods) - 1)

    def get_results(self):
        return (self.result,) + tuple(self.other_values)
    @staticmethod
    def search_ip_address(mac):
        try:    
            session = winrm.Session("10.100.10.100", auth=("asuh\mostafa.m", "Sasa@6266"), transport='ntlm')
            result = session.run_ps(f"Get-DhcpServerv4Scope | Get-DhcpServerv4Lease -EA SilentlyContinue -ClientId {mac}")
            output = result.std_out.decode('utf-8')
            # Define a regular expression pattern to match IP addresses
            ip_and_hostname_pattern = r'(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})\s+.*\s+(\S+)\s+Active'

            # Use re.findall to find all IP addresses in the output
            matches = re.findall(ip_and_hostname_pattern, output)

            for match in matches:
                ip_address, hostname = match
                return f"IP Address: {ip_address}, HostName: {hostname}"
        except:
            return None
class Hospital_search:
    @staticmethod
    def search_department(mac, building_id):
        global stop_event
        vendor_list = ["cisco_ios", "hp_procurve", "cisco_ios_telnet"]
        department_building = Building.objects.filter(id=building_id).first()
        if not department_building:
            return None

        for switch_data in Switching.objects.filter(building=department_building):
            if stop_event.is_set():  # Check if stop_event is set at the start of each loop
                return None

            if switch_data.vendor in vendor_list:
                ip = switch_data.ip_address
                search_result = Search.search_mac_address(ip, mac)
                if search_result:
                    stop_event.set()  # Set the event   to signal other threads to stop
                    return search_result

        return None
class Hospital_buildings:
    @staticmethod
    def gastroo(mac):
       return Hospital_search.search_department(mac, 1)
    @staticmethod
    def surgery(mac):
        return Hospital_search.search_department(mac, 2)
    @staticmethod
    def toxins   (mac):
        return Hospital_search.search_department(mac, 5)
    @staticmethod
    def psychiatric  (mac):
        return Hospital_search.search_department(mac, 6)
    @staticmethod
    def Oncology (mac):
        return Hospital_search.search_department(mac, 7)
    @staticmethod
    def Dental (mac):
        return Hospital_search.search_department(mac, 8)
    @staticmethod
    def Research (mac):
        return Hospital_search.search_department(mac, 9)
    @staticmethod
    def Gynecology (mac):
        return Hospital_search.search_department(mac, 10)
    @staticmethod
    def card(mac):
        return Hospital_search.search_department(mac, 11)
    @staticmethod
    def new_Pediatrics(mac):
       return Hospital_search.search_department(mac, 12)
    @staticmethod
    def TEEC (mac):
       return Hospital_search.search_department(mac, 13)
    @staticmethod
    def Elderly (mac):
       return Hospital_search.search_department(mac, 14)  
    @staticmethod
    def old_Pediatrics (mac):
       return Hospital_search.search_department(mac, 15)
    @staticmethod
    def resonance(mac):
        return Hospital_search.search_department(mac, 16)
    @staticmethod
    def fala7(mac):
        return Hospital_search.search_department(mac, 17)
    def building (mac):
        return Hospital_search.search_department(mac , 18)
    def building2 (mac):
        return Hospital_search.search_department(mac,19)
class Git_mac_address_table:
    def __init__(self) -> None:
        switches = Switching.objects.all()
        for switch_model in switches:
            device = {
                'device_type': switch_model.vendor,
                'host': switch_model.ip_address,
                'username': 'asuh',
                'password': 'password',
                'secret': 'password',
            }

           
            if switch_model.vendor in ["cisco_ios", "cisco_ios_telnet"]:
                try:
                    with ConnectHandler(**device) as switch_connection:
                        switch_connection.enable()
                        non_access_ports = self.get_non_access_ports(switch_connection)
                        mac_table = self.execute_mac_address_table_command_from_cisco(switch_connection, non_access_ports)

                except :
                    pass

            elif switch_model.vendor == "hp_procurve":
                try:
                    mac_table= self.execute_mac_address_table_command_from_hp(switch_model) 
                except Exception as e:
                    pass

            if mac_table:
                switch_model.mac_addresses_tables = mac_table
                switch_model.save()
                mac_table = None
            else:
                pass



    @staticmethod
    def format_interface_name(interface_name):
        parts = interface_name.split()
        if len(parts) > 1:
            if parts[1].startswith("GigabitEthernet"):
                return "Gi" + parts[1][len("GigabitEthernet"):]
            elif parts[1].startswith("FastEthernet"):
                return "Fa" + parts[1][len("FastEthernet"):]
    @staticmethod   
    def get_non_access_ports(switch):
        command = "show running-config | include interface|switchport mode access"
        output = switch.send_command(command)
        non_access_ports = []
        current_port = None

        for line in output.splitlines():
            if line.startswith("interface"):
                if current_port and "switchport mode access" not in current_port:
                    short_name = Git_mac_address_table.format_interface_name(current_port)
                    if short_name:
                        non_access_ports.append(short_name)
                current_port = line
            elif "switchport mode access" in line:
                current_port += " " + line

        if current_port and "switchport mode access" not in current_port:
            short_name = Git_mac_address_table.format_interface_name(current_port)
            if short_name:
                non_access_ports.append(short_name)

        return non_access_ports

    @staticmethod
    def execute_mac_address_table_command_from_cisco(switch, ports):
        ports_string = "|".join(ports)
        command = f"show mac address-table | exclude {ports_string}"
        try:
            # Increase read_timeout if necessary
            output = switch.send_command(command)
            return output
        except Exception as e:
            return None



    @staticmethod
    def get_mac_table_for_switch(switch , comand):
        device = {
            'device_type': switch.vendor,
            'host': switch.ip_address,
            'username': 'asuh',
            'password': 'password',
            'secret': 'password',
        }
        try:
            with ConnectHandler(**device) as net_connect:
                net_connect.enable()
                return net_connect.send_command(comand)
        except Exception as e:
            return None
    @staticmethod
    def execute_mac_address_table_command_from_hp(switch):
        device = {
    'device_type': switch.vendor,  
    'ip': switch.ip_address,              
    'username': 'asuh',          
    'password': 'password', 
    'secret' : 'password',
     }

# Connect to the device
        net_connect = ConnectHandler(**device)

        # Get tagged ports
        output = net_connect.send_command('sh run | exclude untagged')
        pattern = re.compile(r'tagged\s+([\d,-]+)')
        matches = pattern.findall(output)

        # Determine the ports to exclude
        exclude_ports = set()
        for match in matches:
            ports = match.split(',')
            for port in ports:
                if '-' in port:
                    start, end = port.split('-')
                    for p in range(int(start), int(end) + 1):
                        exclude_ports.add(p)
                else:
                    exclude_ports.add(int(port))

        # Fetch the MAC address table
        mac_table = net_connect.send_command('show mac-address')

        # List to store guest MAC addresses
        guest_mac_addresses = []

        # Process the MAC address table
        for line in mac_table.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                mac_address, port, vlan = parts[:3]
                # Check if the port is not in the excluded list and VLAN is the guest VLAN
                if port.isdigit() and int(port) not in exclude_ports : 
                    guest_mac_addresses.append(mac_address)

        # Disconnect from the switch
        net_connect.disconnect()

        # Output the list of guest MAC addresses
        return guest_mac_addresses


def to_dot_format(mac_address):
    # Assuming the input format is 00-00-00-00-00-00
    mac = re.sub('[^a-fA-F0-9]', '', mac_address.lower())
    # Convert to fe9c.ba69.f80d format
    return '.'.join(mac[i:i+4] for i in range(0, 12, 4))

def to_dash_format(mac_address):
    # Assuming the input format is 00-00-00-00-00-00
    mac = re.sub('[^a-fA-F0-9]', '', mac_address.lower())
    # Convert to 000832-6260c0 format
    return mac[:6] + '-' + mac[6:]


def find_mac_address_fromDB(mac_to_search):
    dot_format_mac = to_dot_format(mac_to_search)
    dash_format_mac = to_dash_format(mac_to_search)

    switches_with_mac = []
    for switch in Switching.objects.all():
        mac_addresses = switch.mac_addresses_tables
        if mac_addresses:
            if dot_format_mac in mac_addresses or dash_format_mac in mac_addresses:
                switches_with_mac.append(switch.ip_address)
    return switches_with_mac

