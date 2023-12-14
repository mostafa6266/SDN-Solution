# views.py
from django.shortcuts import render
from .models import check_mac_from_core, check_mac_from_all
from django.contrib.auth.decorators import login_required
from mac_address.models import Git_mac_address_table
from backup.models import Run , update_backup
@login_required(login_url="/login/")
def Chek(request):
    action = request.POST.get("action")
    if action == "core_block":
        check_mac_from_core()
    elif action == "all_block":
        check_mac_from_all()
    elif action == "git_mac":
        Git_mac_address_table()
    elif action == "backup":
        Run()
    elif action == "migration":
        update_backup()   

    return render(request, "blocked_mac_address.html")