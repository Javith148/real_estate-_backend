from rest_framework import serializers
from .models import Property_details, Agent, Property_rooms


class Agent_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'

class Property_rooms_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Property_rooms
        fields = '__all__'


class Property_detailsSerializer(serializers.ModelSerializer):
    agent = Agent_Serializer(source='Agent')   
    property_rooms = Property_rooms_Serializer()
    class Meta:
        model = Property_details
        fields = '__all__'

