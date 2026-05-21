from urllib.parse import quote_plus


def search_youtube(query: str, limit: int = 4):
    if not query.strip():
        return []
    from yt_dlp import YoutubeDL

    options = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "noplaylist": True,
    }
    with YoutubeDL(options) as ydl:
        data = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
    results = []
    for entry in data.get("entries") or []:
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
        if len(results) >= limit:
            break
    return results


def is_youtube_embeddable(video_id: str):
    from yt_dlp import YoutubeDL

    options = {
        "quiet": True,
        "skip_download": True,
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    return bool(info.get("playable_in_embed", True)) and info.get("age_limit", 0) == 0


def companion_links(query: str):
    encoded = quote_plus(query)
    return [
        {
            "label": "圖片搜尋",
            "description": f"看看 {query} 的照片、造型和活動圖。",
            "url": f"https://www.google.com/search?tbm=isch&q={encoded}",
        },
        {
            "label": "影片搜尋",
            "description": f"找 {query} 的舞台、訪談和可愛片段。",
            "url": f"https://www.youtube.com/results?search_query={encoded}",
        },
        {
            "label": "近況搜尋",
            "description": f"看看 {query} 最近的公開消息。",
            "url": f"https://www.google.com/search?tbm=nws&q={encoded}",
        },
    ]


def detect_music_or_interest_query(text: str):
    triggers = ["喜歡聽", "喜歡看", "我喜歡", "我最喜歡", "想看", "想聽"]
    if not any(trigger in text for trigger in triggers):
        return ""
    cleaned = text
    for trigger in triggers:
        cleaned = cleaned.replace(trigger, " ")
    for token in ["我", "我們", "真的", "很", "超", "了", "啊", "欸", "啦", "耶"]:
        cleaned = cleaned.replace(token, " ")
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return ""
    return cleaned[:80]
