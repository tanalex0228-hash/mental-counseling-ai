import json
from urllib.parse import quote_plus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.views import ensure_profile
from llm_engine.agents import CounselingOrchestrator

from .forms import ThemeForm
from .markdown_logger import append_message
from .memory import refresh_room_summary
from .models import ChatMessage, ChatRoom, ChatToolCard
from .serializers import ChatRoomSerializer
from .tooling import companion_links, detect_music_or_interest_query, is_youtube_embeddable, search_youtube


@login_required
def chat_home(request, room_id=None):
    profile = ensure_profile(request.user)
    rooms = ChatRoom.objects.filter(user=request.user)
    if room_id:
        room = get_object_or_404(ChatRoom, id=room_id, user=request.user)
    else:
        room = rooms.first() or ChatRoom.objects.create(user=request.user)

    if request.method == "POST":
        user_text = request.POST.get("message", "").strip()
        uploaded_file = request.FILES.get("attachment")
        if user_text or uploaded_file:
            user_message = ChatMessage.objects.create(
                room=room,
                user=request.user,
                role="user",
                content=user_text or "我上傳了一張照片，想請你看看。",
                uploaded_file=uploaded_file,
                token_count=count_tokens(user_text),
            )
            append_message(room, user_message)
            if room.title == "新的諮詢":
                room.title = user_text[:36]
                room.save(update_fields=["title", "updated_at"])
            image_path = resolve_image_context(room, user_message, user_text)
            llm_user_text = build_llm_user_text(room, user_message, user_text, bool(uploaded_file), bool(image_path))
            agent_output = CounselingOrchestrator().run(room, llm_user_text, image_path=image_path)
            assistant_message = ChatMessage.objects.create(
                room=room,
                user=request.user,
                role="assistant",
                content=agent_output.answer,
                token_count=count_tokens(agent_output.answer),
            )
            append_message(room, assistant_message)
            attach_interest_cards(assistant_message, user_text)
            refresh_room_summary(room)
        return redirect("room", room_id=room.id)

    return render(
        request,
        "chat/home.html",
        {
            "profile": profile,
            "rooms": rooms,
            "room": room,
            "messages_list": room.messages.prefetch_related("tool_cards").all(),
            "theme_form": ThemeForm(instance=profile),
        },
    )


@login_required
def new_conversation(request):
    room = ChatRoom.objects.create(user=request.user)
    return redirect("room", room_id=room.id)


@require_POST
@login_required
def update_theme(request):
    profile = ensure_profile(request.user)
    form = ThemeForm(request.POST, instance=profile)
    if form.is_valid():
        form.save()
        messages.success(request, "色調設定已儲存。")
    return redirect(request.POST.get("next") or "chat_home")


@require_http_methods(["POST"])
@login_required
def chat_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid_json"}, status=400)

    user_text = str(payload.get("message", "")).strip()
    if not user_text:
        return JsonResponse({"error": "message_required"}, status=400)

    room_id = payload.get("room_id") or payload.get("conversation_id")
    if room_id:
        room = get_object_or_404(ChatRoom, id=room_id, user=request.user)
    else:
        room = ChatRoom.objects.create(user=request.user)

    user_message = ChatMessage.objects.create(
        room=room,
        user=request.user,
        role="user",
        content=user_text,
        token_count=count_tokens(user_text),
    )
    append_message(room, user_message)
    if room.title == "新的諮詢":
        room.title = user_text[:36]
        room.save(update_fields=["title", "updated_at"])
    agent_output = CounselingOrchestrator().run(room, user_text)
    assistant_message = ChatMessage.objects.create(
        room=room,
        user=request.user,
        role="assistant",
        content=agent_output.answer,
        token_count=count_tokens(agent_output.answer),
    )
    append_message(room, assistant_message)
    refresh_room_summary(room)

    return JsonResponse(
        {
            "room_id": room.id,
            "conversation_id": room.id,
            "message": user_text,
            "answer": agent_output.answer,
            "classification": agent_output.classification,
            "safety_label": agent_output.safety_label,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def room_list_api(request):
    rooms = ChatRoom.objects.filter(user=request.user)
    return Response(ChatRoomSerializer(rooms, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def youtube_search_api(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return Response({"results": []})

    try:
        from yt_dlp import YoutubeDL

        options = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "noplaylist": True,
        }
        with YoutubeDL(options) as ydl:
            data = ydl.extract_info(f"ytsearch6:{query}", download=False)
        entries = data.get("entries") or []
        results = []
        for entry in entries:
            video_id = entry.get("id")
            if not video_id or len(video_id) != 11:
                continue
            try:
                if not is_youtube_embeddable(video_id):
                    continue
            except Exception:
                continue
            results.append(
                {
                    "id": video_id,
                    "title": entry.get("title") or "Untitled",
                    "channel": entry.get("channel") or entry.get("uploader") or "",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )
            if len(results) >= 4:
                break
        return Response({"results": results})
    except Exception as exc:
        return Response({"error": str(exc), "results": []}, status=502)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def companion_search_api(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return Response({"query": "", "links": []})

    encoded = quote_plus(query)
    links = [
        {
            "label": "YouTube 影片",
            "description": f"搜尋 {query} 的舞台、訪談、可愛片段或歌聲。",
            "url": f"https://www.youtube.com/results?search_query={encoded}",
        },
        {
            "label": "圖片搜尋",
            "description": f"搜尋 {query} 的照片、造型和活動圖。",
            "url": f"https://www.google.com/search?tbm=isch&q={encoded}",
        },
        {
            "label": "新聞與近況",
            "description": f"看看 {query} 最近的公開消息。",
            "url": f"https://www.google.com/search?tbm=nws&q={encoded}",
        },
    ]
    return Response({"query": query, "links": links})


def count_tokens(text: str) -> int:
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        return max(1, len(text) // 4)


def attach_interest_cards(message: ChatMessage, user_text: str):
    query = detect_music_or_interest_query(user_text)
    if not query:
        return
    try:
        videos = search_youtube(query, limit=4)
    except Exception:
        videos = []
    links = companion_links(query)
    if videos:
        ChatToolCard.objects.create(
            message=message,
            card_type="youtube",
            title=f"我幫你找了和「{query}」相關的影片",
            payload={"query": query, "videos": videos},
        )
    ChatToolCard.objects.create(
        message=message,
        card_type="image_links",
        title=f"也可以看看「{query}」的照片和近況",
        payload={"query": query, "links": links},
    )


def resolve_image_context(room: ChatRoom, current_message: ChatMessage, user_text: str) -> str:
    if current_message.uploaded_file:
        return current_message.uploaded_file.path

    photo_terms = [
        "照片",
        "圖片",
        "圖中",
        "照片裡",
        "幾個人",
        "幾位",
        "男生",
        "女生",
        "穿什麼",
        "顏色",
        "合照",
    ]
    if not any(term in user_text for term in photo_terms):
        return ""

    recent_image = (
        room.messages.filter(user=room.user)
        .exclude(uploaded_file="")
        .order_by("-created_at")
        .first()
    )
    return recent_image.uploaded_file.path if recent_image and recent_image.uploaded_file else ""


def build_llm_user_text(
    room: ChatRoom,
    current_message: ChatMessage,
    user_text: str,
    has_new_upload: bool,
    has_image_context: bool,
) -> str:
    base_text = user_text or current_message.content
    if not has_image_context:
        return base_text

    previous_user_messages = (
        room.messages.filter(role="user")
        .exclude(id=current_message.id)
        .order_by("-created_at")[:6]
    )
    previous_context = "\n".join(
        f"- {message.content}" for message in reversed(list(previous_user_messages)) if message.content
    )

    if has_new_upload:
        instruction = (
            "使用者這一輪上傳了一張照片。請把照片視為同一聊天室前文的延伸，"
            "結合前面使用者提到的背景、事件、情緒與關係脈絡來回答。"
            "不要重新問『這是什麼』；如果前文已說明背景，請直接連結照片細節與前文脈絡。"
        )
    else:
        instruction = (
            "使用者正在追問同一聊天室最近上傳的照片。請沿用那張照片與前文脈絡回答，"
            "不要說你看不到照片，也不要要求使用者重新描述。"
        )

    if previous_context:
        return f"{base_text}\n\n{instruction}\n\n同聊天室前文重點：\n{previous_context}"
    return f"{base_text}\n\n{instruction}"
