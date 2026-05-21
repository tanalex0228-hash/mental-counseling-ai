import base64
import mimetypes

from django.conf import settings


class OpenAIClient:
    def complete(self, system_prompt: str, user_text: str, image_path: str = "") -> str:
        if not settings.OPENAI_API_KEY:
            return self._fallback(user_text)

        try:
            from openai import OpenAI

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            user_content = user_text
            if image_path:
                mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
                with open(image_path, "rb") as image_file:
                    encoded = base64.b64encode(image_file.read()).decode("utf-8")
                user_content = [
                    {"type": "text", "text": user_text or "請看看這張照片，溫柔地描述你觀察到的情緒、氛圍和可能的故事。不要辨識真實身分。"},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded}"}},
                ]

            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.45,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            return self._fallback(user_text, error=str(exc))

    def _fallback(self, user_text: str, error: str = "") -> str:
        notice = f"模型暫時無法連線，先使用本地原型回應。原因：{error}\n\n" if error else "目前還沒有設定 OpenAI API Key，所以這是本地原型回應。\n\n"
        return (
            f"{notice}我先陪你把這段話放穩一點：「{user_text[:120]}」。"
            "你可以先試著分成三格寫下來：我現在最強烈的感受是什麼、這個感受通常在什麼情境被拉高、"
            "今天我能做的一個很小的照顧動作是什麼。"
        )
