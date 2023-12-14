from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Switching, Building
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login  # Rename the imported login function
from pages.models import Switching
from blocked_mac.models import Blocked_Mac_Address
from django.http import JsonResponse
from django.shortcuts import redirect
from .forms import SwitchForm

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Use the renamed login function
                # User successfully logged in, you can redirect to a different page
                return redirect("home")
            else:
                # Authentication failed, you can handle this as needed
                return render(request, "lgin.html", {"error_message": "Invalid credentials"})
    
    # If the method is not POST or authentication failed, render the login page.
    return render(request, "lgin.html")



@login_required(login_url="/login/")
def homepage(request):
    core_switches = Switching.objects.filter(description='core')
    distribution_switches = Switching.objects.filter(description='distribution')
    other_switches = Switching.objects.exclude(description__in=['core', 'distribution'])
    
    core_up_count = core_switches.filter(status='UP').count()
    distribution_up_count = distribution_switches.filter(status='UP').count()
    other_up_count = other_switches.filter(status='UP').count()
    
    core_percentage_up = (core_up_count / core_switches.count()) * 100 if core_switches.count() > 0 else 0
    distribution_percentage_up = (distribution_up_count / distribution_switches.count()) * 100 if distribution_switches.count() > 0 else 0
    other_percentage_up = (other_up_count / other_switches.count()) * 100 if other_switches.count() > 0 else 0
    
    context = {
        'core_up_count': core_up_count,
        'core_total_count': core_switches.count(),
        'distribution_up_count': distribution_up_count,
        'distribution_total_count': distribution_switches.count(),
        'other_up_count': other_up_count,
        'other_total_count': other_switches.count(),
        'core_percentage_up': core_percentage_up,
        'distribution_percentage_up': distribution_percentage_up,
        'other_percentage_up': other_percentage_up,
        'blocked_Mac': Blocked_Mac_Address.objects.all().count(),
    }
    
    return render(request, "home.html", context)



@login_required(login_url="/login/")
def switch(request):
    if request.method == "POST":
        form = SwitchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/switching')  # Redirect after POST
    else:
        form = SwitchForm()  # An unbound form
    buildings_with_switches = []
    for building in Building.objects.all():
        switches = Switching.objects.filter(building=building)
        total_switches = switches.count()
        up_switches = switches.filter(status='UP').count()
        down_switches = switches.filter(status='DOWN').count()

        buildings_with_switches.append({
            'building': building,
            'switches': switches,
            'total_switches': total_switches,
            'up_switches': up_switches,
            'down_switches': down_switches
        })
    context = {
        "buildings": buildings_with_switches,
        "form": form  # Include the form in the context
    }
    return render(request, "switch_data.html", context)


    

    

@login_required(login_url="/login/")
def building_detail(request, building_id):
    building = get_object_or_404(Building, pk=building_id)
    switchings = Switching.objects.filter(building=building)
    return render(request, "building_detail.html", {"building": building, "switchings": switchings})




def get_switches(request):
    # Get the category from the request parameters
    category = request.GET.get('category', '')

    # Filter switches based on the category
    if category == 'core':
        switches = Switching.objects.filter(description='core')
    elif category == 'distribution':
        switches = Switching.objects.filter(description='distribution')
    else:
        switches = Switching.objects.exclude(description__in=['core', 'distribution'])

    # Prepare data to be JSON-serialized
    switches_data = [{
        'name': switch.name,
        'ip_address': switch.ip_address,
        'building': switch.building.name if switch.building else 'N/A',
        'status': switch.status
    } for switch in switches]

    # Return the data as JSON
    return JsonResponse({'switches': switches_data})