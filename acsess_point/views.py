from django.shortcuts import render, redirect
from .forms import  AccessPointForm
from pages.models import Building , Switching
from .models import AccessPoint
from blocked_mac.models import block_from_core , Blocked_Mac_Address , Change_vlan , Display_vlan , ShutdownPort , NoShutdownPort
from mac_address.models import find_mac_address_fromDB , Return_result , Search 
from django.http import HttpResponseNotModified
from mac_address.views import parse_mac_table


def access_points_view(request):
    if request.method == 'POST':
        access_point_form = AccessPointForm(request.POST, prefix="access_point")
        if 'submit_access_point' in request.POST and access_point_form.is_valid():
            access_point_form.save()
            return redirect('/acsess_point')  # Redirect to the same view or another appropriate view
        elif 'submit_access_point' in request.POST and not access_point_form.is_valid():
            raise HttpResponseNotModified("Form data is invalid")
    else:
        access_point_form = AccessPointForm(prefix="access_point")

    buildings = Building.objects.prefetch_related('accesspoint_set').all()
    context = {
        'buildings': buildings,
        'access_point_form': access_point_form,
    }
    return render(request, 'add_all.html', context)

def acsess_data(request, pk):
   
    print(request.POST.get('action'))
    mac_data = None
    acsess = AccessPoint.objects.get(pk=pk)
    display = False
    
    if request.method == 'POST':
        action = request.POST.get('action')

        # Update mac_data for all actions if mac_address is available
        mac_address = acsess.mac_address      
        if mac_address:
            mac_data = find_and_search_mac(mac_address)
            display = True
            device_ip = mac_data['device_ip']
            port = mac_data['port']
        
        if action == 'Block in core':
            block_from_core(acsess.mac_address, acsess.vlan)
            Blocked_Mac_Address.objects.create(mac_address=acsess.mac_address, vlan=acsess.vlan, reason='acsess point')
            
        elif action == 'Assign to VLAN':
            vlan_number = request.POST.get('vlan_number')
            if mac_data and vlan_number:
                # Assuming Change_vlan function takes VLAN number as an argument
                Change_vlan(mac_data['device_ip'], mac_data['port'], vlan_number)
                acsess.vlan = vlan_number
                acsess.save()
        elif action == 'Show MAC Address':
            if device_ip and port:
                vlan_display = Display_vlan(device_ip, port)
                output = vlan_display.output
                vendor = vlan_display.switch.vendor if vlan_display.switch else 'unknown'
                
                mac_table = parse_mac_table(output, vendor)
                context = {
                    'acsess': acsess,
                    'mac_data': mac_data ,
                    'display':display,
                    "mac_table": mac_table ,  
                    "port": port
                    }
                return render(request, 'acsess_data.html', context)
        elif action == 'shutdown port':
            acsess.port_status = 'Shutdown'
            acsess.real_port = port
            acsess.switch_ip = device_ip
            ShutdownPort(device_ip , port)
            if ShutdownPort:
                acsess.save()
        elif action =='no shutdown port':
            if acsess.switch_ip and acsess.real_port:
                print(acsess.switch_ip , acsess.real_port)
                NoShutdownPort(acsess.switch_ip , acsess.real_port)
                if NoShutdownPort:
                    acsess.port_status = 'enable'
                    display = False
                    acsess.save()



    context = {
        'acsess': acsess,
        'mac_data': mac_data,
        'display':display,
    }
    print (display)
    return render(request, 'acsess_data.html', context)





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
                switch = Switching.objects.filter(ip_address=device_ip).first()
                vendor = switch.vendor if switch else "Unknown"
    except:      
        pass  
    result_instance = Return_result(mac)
    if result_instance :               
        
        results = result_instance.get_results()
        if results:
                port, vlan, device_ip = handle_results(results)

                description, building_name = get_switch_details(device_ip) if device_ip else ("Unknown", "Unknown")
                switch = Switching.objects.filter(ip_address=device_ip).first()
                vendor = switch.vendor if switch else "Unknown"
                return  {
                    "blocked": False,
                    "mac_address": mac,
                    "port": port,
                    "vlan": vlan,
                    "device_ip": device_ip,
                    "description": description,
                    "building_name": building_name,
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








