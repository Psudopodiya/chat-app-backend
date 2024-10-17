from django.contrib import admin
from .models import ChatRoom, ChatMessage


# Register your models here.

class ChatRoomAdmin(admin.ModelAdmin):
    filter_horizontal = ('participants',)


admin.site.register(ChatRoom, ChatRoomAdmin)
admin.site.register(ChatMessage)
