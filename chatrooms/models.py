from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class ChatRoom(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owned_rooms')
    participants = models.ManyToManyField(CustomUser, related_name='rooms', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
