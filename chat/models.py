from django.conf import settings
from django.db import models


class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, default="新的諮詢")
    summary = models.TextField(blank=True)
    markdown_transcript = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "使用者"),
        ("assistant", "助理"),
        ("system", "系統"),
    ]

    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"


class KnowledgeDocument(models.Model):
    DOC_TYPES = [
        ("policy", "回答規範"),
        ("skill", "諮商技能"),
        ("category", "生活情境分類"),
        ("guardrail", "臨床安全規則"),
        ("source_note", "來源筆記"),
    ]

    title = models.CharField(max_length=160)
    doc_type = models.CharField(max_length=24, choices=DOC_TYPES)
    category = models.CharField(max_length=80, blank=True)
    source_type = models.CharField(max_length=80, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    vector_index_id = models.CharField(max_length=120, blank=True)
    tags = models.CharField(max_length=240, blank=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["doc_type", "title"]

    def __str__(self):
        return self.title


class ChatRoom(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, default="新的諮詢")
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "使用者"),
        ("assistant", "助理"),
        ("system", "系統"),
    ]

    room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    uploaded_file = models.FileField(upload_to="chat_uploads/%Y/%m/%d/", blank=True)
    markdown_backup_path = models.CharField(max_length=500, blank=True)
    token_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"


class ChatToolCard(models.Model):
    CARD_TYPES = [
        ("youtube", "YouTube"),
        ("image_links", "圖片連結"),
        ("checklist", "清單"),
    ]

    message = models.ForeignKey(ChatMessage, related_name="tool_cards", on_delete=models.CASCADE)
    card_type = models.CharField(max_length=32, choices=CARD_TYPES)
    title = models.CharField(max_length=160)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.card_type}: {self.title}"


class UserMemory(models.Model):
    MEMORY_TYPES = [
        ("preference", "偏好"),
        ("context", "諮商脈絡"),
        ("summary", "長期摘要"),
        ("risk", "風險提醒"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="memories", on_delete=models.CASCADE)
    memory_type = models.CharField(max_length=32, choices=MEMORY_TYPES, default="context")
    content = models.TextField()
    importance_score = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-importance_score", "-updated_at"]

    def __str__(self):
        return f"{self.user.username}: {self.memory_type}"
