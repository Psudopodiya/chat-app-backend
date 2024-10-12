from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom
from .serializers import RoomSerializer, CreateRoomSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@api_view(['GET'])
def list_rooms(request):
    rooms = ChatRoom.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_room(request):
    serializer = CreateRoomSerializer(data=request.data)
    if serializer.is_valid():
        room = serializer.save(owner=request.user)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "rooms",
            {
                "type": "room_created",
                "message": RoomSerializer(room).data
            }
        )
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes(['IsAuthenticated'])
def join_room(request, room_id):
    if request.user.is_authenticated:
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return Response({'detail': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

        room.participants.add(request.user)
        room.save()
        return Response({'detail': f'Joined room {room.title}'}, status=status.HTTP_200_OK)
    return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)