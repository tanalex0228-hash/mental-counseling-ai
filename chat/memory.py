from .models import ChatRoom, UserMemory


def recent_history(room: ChatRoom, limit: int = 20) -> str:
    messages = room.messages.order_by("-created_at")[:limit]
    ordered = reversed(list(messages))
    lines = []
    for message in ordered:
        attachment = " [包含一張使用者上傳的圖片]" if message.uploaded_file else ""
        lines.append(f"{message.role}{attachment}: {message.content}")
    return "\n".join(lines)


def long_term_memory(user, limit: int = 6) -> str:
    memories = UserMemory.objects.filter(user=user)[:limit]
    return "\n".join(f"- {memory.memory_type}: {memory.content}" for memory in memories)


def refresh_room_summary(room: ChatRoom):
    messages = list(room.messages.order_by("-created_at")[:6])
    if not messages:
        return
    snippets = [message.content[:80] for message in reversed(messages)]
    room.summary = " / ".join(snippets)[-1000:]
    room.save(update_fields=["summary", "updated_at"])
