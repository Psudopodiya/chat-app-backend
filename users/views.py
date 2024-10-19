from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, EditProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from chatrooms.models import ChatRoom

CustomUser = get_user_model()


@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        public_rooms = ChatRoom.objects.filter(room_type='public')

        for room in public_rooms:
            room.participants.add(user)

        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def profile(request):
    if request.user.is_authenticated:
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PUT', 'POST'])
def edit_profile(request):
    if request.user.is_authenticated:
        user = request.user
        serializer = EditProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def list_users(request):
    if request.user.is_authenticated:
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        response_list = []
        for data in serializer.data:
            if not data.get('username') == request.user.username:
                response_list.append(data.get('username'))
        return Response(response_list, status=status.HTTP_200_OK)
    return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
