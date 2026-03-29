from django.shortcuts import render
from .models import Property_details, Agent, Property_rooms
from .serializers import Property_detailsSerializer, Agent_Serializer, Property_rooms_Serializer
from rest_framework.decorators import api_view
from rest_framework.response import Response



@api_view(['GET'])
def property_details_api(request):
    property = Property_details.objects.all()
    convert_api = Property_detailsSerializer(property, many=True)
    return Response(convert_api.data)