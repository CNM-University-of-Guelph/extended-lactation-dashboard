from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import LactationData, MultiparousFeatures, PrimiparousFeatures

class UserSerializer(serializers.ModelSerializer):
    confirmPassword = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    class Meta:
        model = User     
        fields = ["id", "username", "email", "password", "confirmPassword"]
        extra_kwargs = {
            "password": {"write_only": True}, # Prevent passwords from being exposed in API
            "confirmPassword": {"write_only": True},          
           }

    def validate_email(self, value):
        """
        Check that the email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, data):
        """
        Check that the passwords match.
        """
        password = data.get("password")
        confirmPassword = data.get("confirmPassword")

        if password != confirmPassword:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("confirmPassword", None)
        user = User.objects.create_user(**validated_data)
        return user
 

class LactationDataSerializer(serializers.ModelSerializer):
    cow_id = serializers.CharField(source='lactation.cow.cow_id')
    parity = serializers.IntegerField(source='lactation.parity')

    class Meta:
        model = LactationData
        fields = ['cow_id', 'parity', 'dim', 'date', 'milk_yield']


class MultiparousFeaturesSerializer(serializers.ModelSerializer):
    cow_id = serializers.CharField(source='lactation.cow.cow_id')
    parity = serializers.IntegerField(source='lactation.parity')

    class Meta:
        model = MultiparousFeatures
        fields = '__all__'


class PrimiparousFeaturesSerializer(serializers.ModelSerializer):
    cow_id = serializers.CharField(source='lactation.cow.cow_id')
    parity = serializers.IntegerField(source='lactation.parity')

    class Meta:
        model = PrimiparousFeatures
        fields = '__all__'
        