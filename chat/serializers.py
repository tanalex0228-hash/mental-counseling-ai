from rest_framework import serializers

from .models import ChatMessage, ChatRoom


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ("id", "title", "summary", "created_at", "updated_at")


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ("id", "room", "role", "content", "markdown_backup_path", "token_count", "created_at")
        read_only_fields = ("role", "markdown_backup_path", "token_count", "created_at")
