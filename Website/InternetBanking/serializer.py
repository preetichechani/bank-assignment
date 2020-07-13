from rest_framework import serializers
from django.db import transaction
from .models import User,Account, TransactionHistory

class userSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

class accountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = '__all__'

class TransactionHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionHistory
        fields = '__all__'
