from django.db import models
from pages.models import Switching , Building
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from netmiko import ConnectHandler ,  NetMikoTimeoutException, NetMikoAuthenticationException
from pythonping import ping



# Create your models here.

def send_telegram_message( message):
    """
    Sends a message to a specified Telegram chat using a bot.
    """
    bot_token = "Your bot_token "
    chat_id = "your chat_id"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()

class RunMonitoring:
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


class SwitchMonitor:
    def __init__(self, building_id) -> None:
        self.building_id = building_id
        department_building = Building.objects.filter(id=building_id).first()
        for switch_data in Switching.objects.filter(building=department_building):
            if switch_data.vendor in ["hp_procurve", "cisco_ios", "cisco_s300" , "extreme" ,"cisco_ios_telnet" , "foundry_telnet"]  :
                self.monitor_cli_switch(switch_data)
            else:
                self.monitor_gui_switch(switch_data)

    def monitor_cli_switch(self, switch_data):
        device = {
            'device_type': switch_data.vendor,  
            'host': switch_data.ip_address,
            'username': 'user',
            'password': 'password',
            'secret': 'password',  
        }

        try:
            with ConnectHandler(**device) as  conect:
                conect.disconnect()
                switch_status = "UP"
        except (NetMikoTimeoutException, NetMikoAuthenticationException, Exception) as e:
            try:
                response = ping(switch_data.ip_address, count=2, verbose=False)
                timeouts = sum(1 for reply in response if not reply.success)
                if response.packets_lost == 2 or timeouts == 2:
                    switch_status = "DOWN"
                else:
                    switch_status = "UP"
            except Exception as e:
                switch_status = "DOWN"

        if switch_data.status != switch_status:
            print(f"-------------///////////////////////////Alarm: Status of switch {switch_data.ip_address} changed to {switch_status}------------------////////////////") 
            send_telegram_message(f'Switch name is :- {switch_data.name} In {switch_data.building}\nAlarm: Status of switch {switch_data.ip_address} \n Changed to {switch_status}')

        switch_data.status = switch_status
        switch_data.save()
        switch_status = None

    def monitor_gui_switch(self, switch_data):
       
        try:
            requests.get(switch_data.website, timeout=10)
            
            switch_status = "UP"
        except Exception as e:
            try:
                response = ping(switch_data.ip_address, count=2, verbose=False)
                timeouts = sum(1 for reply in response if not reply.success)
                if response.packets_lost == 2 or timeouts == 2:
                    switch_status = "DOWN"
                else:
                    switch_status = "UP"
            except Exception as e:
                switch_status = "DOWN"

        if switch_data.status != switch_status:
            print(f"-------------///////////////////////////Alarm: Status of switch {switch_data.ip_address} changed to {switch_status}------------------////////////////") 
            send_telegram_message(f'Switch name is :- {switch_data.name} In {switch_data.building}\nAlarm: Status of switch {switch_data.ip_address} \n Changed to {switch_status}')
            switch_data.status = switch_status
            switch_data.save()
        switch_status = None





class Action_to_switch:
    @staticmethod
    def gastroo():
       return SwitchMonitor(1)
    @staticmethod
    def surgery():
        return SwitchMonitor(2)
    @staticmethod
    def toxins ():
         SwitchMonitor(5)
         SwitchMonitor(6)
    @staticmethod
    def Oncology ():
         SwitchMonitor(7)
         SwitchMonitor(8)
         SwitchMonitor(9)
         SwitchMonitor(10)
    @staticmethod
    def card():
         SwitchMonitor(11)
    @staticmethod
    def new_Pediatrics():
        SwitchMonitor(12)
    @staticmethod
    def TEEC ():
        SwitchMonitor(13)
        SwitchMonitor(14)  
        SwitchMonitor(15)
        SwitchMonitor(16)
        SwitchMonitor(17)
    def building ():
        SwitchMonitor(18)
        SwitchMonitor(19)    