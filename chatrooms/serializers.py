from rest_framework import serializers
from .models import ChatRoom
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class RoomSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    participants = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'title', 'description', 'owner', 'participants', 'created_at', 'room_type']


class CreateRoomSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(child=serializers.CharField(), write_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = ChatRoom
        fields = ['title', 'description', 'participants', 'owner', "room_type"]

    def create(self, validated_data):
        participants_usernames = validated_data.pop('participants')
        owner = validated_data.pop('owner')
        room = ChatRoom.objects.create(owner=owner, **validated_data)
        room_type = validated_data.get('room_type')

        participants = [owner]

        if room_type == 'public':
            participants += list(User.objects.all())
        else:
            for username in participants_usernames:
                try:
                    user = User.objects.get(username=username)
                    participants.append(user)
                except User.DoesNotExist:
                    raise serializers.ValidationError(f"User '{username}' does not exist.")

        room.participants.set(participants)
        return room

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['participants'] = [user.username for user in instance.participants.all()]
        return representation
