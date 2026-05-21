from pathlib import Path

from django.conf import settings
from django.utils import timezone


def room_log_path(room) -> Path:
    return Path(settings.MARKDOWN_LOG_DIR) / str(room.user_id) / f"{room.id}.md"


def ensure_log_file(room) -> Path:
    path = room_log_path(room)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        created_at = timezone.localtime(room.created_at).strftime("%Y-%m-%d %H:%M")
        path.write_text(
            "\n".join(
                [
                    f"# Chat Room: {room.title}",
                    "",
                    "## Metadata",
                    "",
                    f"- User ID: {room.user_id}",
                    f"- Room ID: {room.id}",
                    f"- Created At: {created_at}",
                    f"- Updated At: {created_at}",
                    "",
                    "---",
                    "",
                    "## Conversation",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return path


def append_message(room, message):
    path = ensure_log_file(room)
    timestamp = timezone.localtime(message.created_at).strftime("%Y-%m-%d %H:%M")
    role = "User" if message.role == "user" else "Assistant" if message.role == "assistant" else "System"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"### {role} - {timestamp}\n\n{message.content}\n\n")
    message.markdown_backup_path = str(path)
    message.save(update_fields=["markdown_backup_path"])
    return path
