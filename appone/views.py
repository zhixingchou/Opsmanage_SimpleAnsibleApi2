#coding: utf-8
from django.shortcuts import render
from .models import Asset
from .forms import AssetForm
from django.template import RequestContext
from django.http import JsonResponse

from ansible_interface import AnsiInterface

# Create your views here.


from django.shortcuts import render

# Create your views here.


def add_assetip(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = AssetForm()

    return render(request, 'add_assetip.html', {'form':form})


def update_asset(request):
    asset = Asset.objects.all()
    return render(request,'update_asset.html',{"asset":asset})


def asset_fact(request):
    asset_ip = request.POST.get('ip')
    server_asset = Asset.objects.get(ip=request.POST.get('ip'))
    # resource = [{"hostname": server_asset.ip, "port": server_asset.port, "username": server_asset.username,
    #              "password": server_asset.passwd}]

    resource = [{"hostname": server_asset.ip, "port": "22", "username": "root", "password": "password",
         "ip": server_asset.ip}]

    interface = AnsiInterface(resource)
    data = interface.handle_cmdb_data(server_asset.ip)
    if data:
        for ds in data:
            status = ds.get('status')
            if status == 0:
                Asset.objects.filter(ip=server_asset.ip).update(cpucore=ds.get('cpu_core'))
        return JsonResponse({'msg': "数据更新成功", "code": 200})






