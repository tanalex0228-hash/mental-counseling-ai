from django.contrib import admin

from .models import ChatMessage, ChatRoom, ChatToolCard, Conversation, KnowledgeDocument, Message, UserMemory


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "updated_at", "created_at")
    search_fields = ("title", "user__username", "markdown_transcript")
    inlines = [MessageInline]


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "doc_type", "category", "source_type", "is_active", "updated_at")
    list_filter = ("doc_type", "category", "source_type", "is_active")
    search_fields = ("title", "tags", "content", "file_path")


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("created_at", "markdown_backup_path", "token_count")


class ChatToolCardInline(admin.TabularInline):
    model = ChatToolCard
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "updated_at", "created_at")
    search_fields = ("title", "user__username", "summary")
    inlines = [ChatMessageInline]


@admin.register(ChatToolCard)
class ChatToolCardAdmin(admin.ModelAdmin):
    list_display = ("title", "card_type", "message", "created_at")
    list_filter = ("card_type",)
    search_fields = ("title", "payload", "message__content")


@admin.register(UserMemory)
class UserMemoryAdmin(admin.ModelAdmin):
    list_display = ("user", "memory_type", "importance_score", "updated_at")
    list_filter = ("memory_type", "importance_score")
    search_fields = ("user__username", "content")
