from rest_framework import serializers
from .models import User,TravelInformation,TravelRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class TravelInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelInformation
        fields = '__all__'

class TravelRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelRequest
        fields = '__all__'

