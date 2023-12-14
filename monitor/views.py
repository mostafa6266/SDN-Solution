from django.shortcuts import render
from pages.models import Switching
from rest_framework.response import Response
from rest_framework.decorators import api_view
from monitor.seriakizer import SwitchesSerializers

@api_view(['GET'])
def test_api(request):
    switch_api = Switching.objects.all()
    switch_list = SwitchesSerializers(switch_api, many=True)
    return Response(switch_list.data)

@api_view(['POST'])
def creat (request):
    serializer = SwitchesSerializers(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors)
    
@api_view(['GET' , 'PUT' , 'DELETE'])
def switch(request , pk):
    swutch = Switching.objects.get(pk = pk)
    if request.method == 'GET':
        serializer = SwitchesSerializers(swutch)
        return Response(serializer.data)
    if request.method == 'PUT':
        serializer = SwitchesSerializers(swutch , data = request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

    if request.method == 'DELETE':
        serializer = SwitchesSerializers(swutch , data = request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
