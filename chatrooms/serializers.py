from rest_framework import serializers
from .models import ChatRoom


class RoomSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    participants = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'title', 'description', 'owner', 'participants', 'created_at']


class CreateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['title', 'description']
