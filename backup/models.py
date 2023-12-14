from django.db import models
from netmiko import ConnectHandler 
from concurrent.futures import ThreadPoolExecutor, as_completed
from pages.models import Switching, Building 
# Create your models here.


class Run:
    def __init__(self) -> None:
        try:
            methods = [getattr(Action_to_switch, func) for func in dir(Action_to_switch)
                       if callable(getattr(Action_to_switch, func)) and not func.startswith("__")]
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(method) for method in methods]
                for future in as_completed(futures):
                    try:
                        result = future.result()
                    except Exception as e:
                        pass
        except Exception as e:
            pass



class Git_backup:
    def __init__(self, building_id) -> None:
        self.building_id = building_id
        department_building = Building.objects.filter(id=building_id).first()
        for switch_data in Switching.objects.filter(building=department_building):
            try:    
                device = {
                    'device_type': switch_data.vendor,
                    'host': switch_data.ip_address,
                    'username': 'user',
                    'password': 'password',
                    'secret': 'password',
                }

                if switch_data.vendor in ["cisco_ios", "hp_procurve", "cisco_ios_telnet" , "cisco_s300" , 'extreme']:
                    
                        with ConnectHandler(**device) as switch_connection:
                            switch_connection.enable()
                            new_backup = switch_connection.send_command("show running-config")

                            # Compare new_backup with existing backup
                            if new_backup != switch_data.backup:
                                # If different, update new_backup field
                                switch_data.new_backup = new_backup
                                switch_data.save()
                            else:
                               pass
                            switch_connection.disconnect()
            except Exception as e:
                    raise Exception(f"Error on switch {switch_data.ip_address}: {e}")
            new_backup = None
                




class Action_to_switch:
    @staticmethod
    def gastroo():
       return Git_backup(1)
    @staticmethod
    def surgery():
        return Git_backup(2)
    @staticmethod
    def toxins   ():
        return Git_backup(5)
    @staticmethod
    def psychiatric  ():
        return Git_backup(6)
    @staticmethod
    def Oncology ():
        return Git_backup(7)
    @staticmethod
    def Dental ():
        return Git_backup(8)
    @staticmethod
    def Research ():
        return Git_backup(9)
    @staticmethod
    def Gynecology ():
        return Git_backup(10)
    @staticmethod
    def card():
        return Git_backup(11)
    @staticmethod
    def new_Pediatrics():
       return Git_backup(12)
    @staticmethod
    def TEEC ():
       return Git_backup(13)
    @staticmethod
    def Elderly ():
       return Git_backup(14)  
    @staticmethod
    def old_Pediatrics ():
       return Git_backup(15)
    @staticmethod
    def resonance():
        return Git_backup(16)
    @staticmethod
    def fala7():
        return Git_backup(17)
    def building ():
        return Git_backup(18)
    def building2 ():
        return Git_backup(19)    



def update_backup():
    # Iterate over all Switching instances
    for switch in Switching.objects.all():
        # Check if there is a new backup
        if switch.new_backup:
            # Copy new_backup to backup
            switch.backup = switch.new_backup
            # Clear new_backup
            switch.new_backup = None
            # Save the changes to the database
            switch.save()
        else:
            pass





