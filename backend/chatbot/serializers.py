from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Conversation, PDF


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = ['description', 'pdf_url', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    pdfs = PDFSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'user', 'created_at', 'pdfs']
