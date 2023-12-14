from django.shortcuts import render 
from .models import Return_result , find_mac_address_fromDB , Search
from pages.models import Switching,Vlan
from django.contrib.auth.decorators import login_required
from blocked_mac.models import Blocked_Mac_Address  , undo_block_from_core , block_from_core , Change_vlan , Blocke_from_switch , Undo_Blocke_from_switch , Display_vlan





@login_required(login_url="/login/")
def result(request):
    message = None
    mac = request.GET.get('mac')
    all_vlans = Vlan.objects.all()

    action = request.POST.get('action')
    if action == "in_switch":
        mac = request.POST.get('mac')
        vlan = request.POST.get('vlan')
        device_ip = request.POST.get('ipaddress')
        reason = request.POST.get('reason')
        message = f'MAC address {mac} has been blocked in {device_ip}.'
        if reason:
            try:
                Blocke_from_switch(device_ip ,mac , vlan )
                Blocked_Mac_Address.objects.create(switch_ip= device_ip, mac_address=mac, vlan=vlan, reason=reason)
                return render(request, "search.html", {"message": message})
            except Exception as e:
                pass
                
                    
    if action == 'block_in_core':
        mac = request.POST.get('mac')
        vlan = request.POST.get('vlan')
        reason = request.POST.get('reason')
        message= f'MAC address {mac} has been blocked in core.'
        if reason:
            try:
                block_from_core(mac, vlan)
                Blocked_Mac_Address.objects.create(switch_ip="192.168.20.1", mac_address=mac, vlan=vlan, reason=reason)
                return render(request, "search.html", {"message": message})
            except Exception as e:
                pass
            

    if action == 'Change_vlan':
        vlan = request.POST.get('vlan')
        device_ip = request.POST.get('ipaddress')
        port = request.POST.get('port')
        message= f'The vlan has been changed to {vlan}'
        if vlan : 
            Change_vlan(device_ip , port , vlan)
            if not Change_vlan:
                message = "erorr"
            return render(request, "search.html", {"message": message})

    if action == "show_mac":
        device_ip = request.POST.get('ipaddress')
        port = request.POST.get('port')
        if device_ip and port:
            vlan_display = Display_vlan(device_ip, port)
            output = vlan_display.output
            vendor = vlan_display.switch.vendor if vlan_display.switch else 'unknown'
            
            mac_table = parse_mac_table(output, vendor)
            return render(request, "search.html", {"mac_table": mac_table ,  "port" : port})
        else:
            message = "error"
            return render(request, "search.html", {"message": message })

        


    if mac:
        blocked_mac = Blocked_Mac_Address.objects.filter(mac_address=mac).all()
        if blocked_mac:
            switch_ip = blocked_mac.first().switch_ip
            action = request.POST.get('action')
            message = f'MAC address {mac} has been unblocked in {switch_ip}.'
            if action == 'undo_block':
                if switch_ip != 'core ip':
                    for mac_entry  in blocked_mac :
                        Undo_Blocke_from_switch(mac_entry.switch_ip, mac_entry.mac_address , mac_entry.vlan)
                        blocked_mac.delete()
                    return render(request, "search.html" , {'message':message})

                else:
                    for mac_entry  in blocked_mac :
                        undo_block_from_core(mac_entry.mac_address, mac_entry.vlan)
                        blocked_mac.delete()
                    
                    return render(request, "search.html" , {'message':message})

            else:
                # MAC is blocked, return with blocked status
                return render(request, "search.html", {
                    "blocked": True,
                    "blocked_mac": blocked_mac,
                    "vlans": all_vlans
                })
       
        # If the MAC address is not blocked, perform the search
        search_result = find_and_search_mac(mac)
        if search_result:
            return render(request, "search.html", search_result)

    # Handle POST request for blocking MAC address
    
        
    

    # Default rendering if no MAC address is provided or other conditions
    return render(request, "search.html", {"vlans": all_vlans})

def find_and_search_mac(mac):
    try:
        switches_with_mac = find_mac_address_fromDB(mac)
        if switches_with_mac:
            ip = switches_with_mac[0]
            search_result = Search.search_mac_address(ip, mac)
            if search_result:
                port = search_result[1]
                vlan = search_result[2]
                device_ip = search_result[3]
                description, building_name = get_switch_details(device_ip) if device_ip else ("Unknown", "Unknown")
                ip_result = Return_result.search_ip_address(mac)
                switch = Switching.objects.filter(ip_address=device_ip).first()
                vendor = switch.vendor if switch else "Unknown"
                
                return {
                    "blocked": False,
                    "mac_address": mac,
                    "port": port,
                    "vlan": vlan,
                    "device_ip": device_ip,
                    "description": description,
                    "building_name": building_name,
                    "vlans": Vlan.objects.all(),
                    "ip_result": ip_result,
                    "vendor": vendor,
                       }
    except:      
        pass  
    result_instance = Return_result(mac)
    if result_instance :               
        
        results = result_instance.get_results()
        if results:
                ip_result = Return_result.search_ip_address(mac)
                port, vlan, device_ip = handle_results(results)

                description, building_name = get_switch_details(device_ip) if device_ip else ("Unknown", "Unknown")
                switch = Switching.objects.filter(ip_address=device_ip).first()
                vendor = switch.vendor if switch else "Unknown"
                return  {
                    "blocked": False,
                    "mac_address": mac,
                    "port": port,
                    "vlan": vlan,
                    "ip_result": ip_result,
                    "device_ip": device_ip,
                    "description": description,
                    "building_name": building_name,
                    "vlans": Vlan.objects.all(),
                    "vendor": vendor,
                }
    return {"mac_address": mac}



def handle_results(results):
    for result in results:
        if result:
            return  result[1], result[2], result[3]  
    return None, None, None

def get_switch_details(device_ip):
    try:
        switch = Switching.objects.get(ip_address=device_ip)
        description = switch.name
        building_name = switch.building.name if switch.building else None
    except Switching.DoesNotExist:
        description = "Unknown"
        building_name = "Unknown"
    return description, building_name


def parse_mac_table(output, vendor):
    lines = output.split('\n')
    mac_table = []

    if vendor in ["cisco_ios", "cisco_ios_telnet"]:
        for line in lines:
            if line and not line.startswith('Vlan') and not line.startswith('----') and not line.startswith('Total'):
                parts = line.split()
                if len(parts) == 4:
                    vlan, mac_address, type_, port = parts
                    mac_table.append({'vlan': vlan, 'mac_address': mac_address, 'type': type_, 'port': port})

    elif vendor == "hp_procurve":
        for line in lines:
            if line and not line.startswith('MAC Address') and not line.startswith('-------------'):
                parts = line.split()
                if len(parts) == 2:
                    mac_address, vlan = parts[0], parts[1]
                    mac_table.append({'vlan': vlan, 'mac_address': mac_address, 'type': 'N/A', 'port': 'N/A'})

    return mac_table










