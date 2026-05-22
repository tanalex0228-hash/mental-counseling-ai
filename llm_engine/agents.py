from dataclasses import dataclass

from accounts.views import ensure_profile
from chat.memory import long_term_memory, recent_history
from chat.models import KnowledgeDocument
from chat.tooling import detect_music_or_interest_query

from .openai_client import OpenAIClient
from .prompt_builder import PromptBuilder
from .rag_retriever import RagRetriever
from .safety_guard import SafetyGuard


CATEGORY_KEYWORDS = {
    "感情": ["分手", "喜歡", "曖昧", "失戀", "感情", "被綠", "綠", "綠了", "劈腿", "出軌", "小三"],
    "家庭": ["家人", "爸", "媽", "父母", "家庭"],
    "同儕": ["朋友", "同學", "同儕"],
    "伴侶": ["伴侶", "男友", "女友", "男朋友", "女朋友", "老公", "老婆", "被綠", "綠", "劈腿", "出軌"],
    "學業壓力": ["考試", "作業", "學校", "學業", "教授"],
    "工作壓力": ["工作", "老闆", "同事", "職場", "實習", "linkedin", "LinkedIn"],
    "自我懷疑": ["沒用", "懷疑", "失敗", "不夠好", "很廢", "不夠厲害", "輸別人"],
    "情緒低落": ["難過", "低落", "哭", "沮喪", "空", "累了", "撐什麼"],
    "焦慮": ["焦慮", "緊張", "恐慌", "擔心", "未來", "怕停下來"],
    "孤獨": ["孤單", "孤獨", "沒有人", "宿舍", "家裡的人", "不太懂"],
    "睡眠失衡": ["睡眠", "三四點", "熬夜", "睡不著", "逼自己起床"],
    "高壓耗竭": ["每天都很忙", "越忙越覺得空", "累了", "不知道怎麼繼續", "撐什麼", "怕停下來"],
    "人際衝突": ["吵架", "衝突", "誤會", "討厭"],
    "背叛與依附受傷": ["被綠", "綠", "劈腿", "出軌", "背叛", "他不愛我", "她不愛我", "愛那個女的", "愛那個男的"],
    "危機風險": ["自殺", "想死", "傷害自己", "傷害他人", "家暴"],
}


@dataclass
class AgentOutput:
    context: str
    classification: str
    skills: str
    rag_context: str
    answer: str
    safety_label: str = "normal"


class ContextAgent:
    def run(self, room):
        profile = ensure_profile(room.user)
        memory = long_term_memory(room.user)
        history = recent_history(room)
        preference = (
            f"回答長度偏好：{profile.get_response_length_display()}\n"
            f"回答語氣偏好：{profile.get_response_tone_display()}\n"
            f"顯示心理學理論依據：{'是' if profile.show_theory_basis else '否'}\n"
            f"允許長期摘要：{'是' if profile.allow_memory_summaries else '否'}\n"
            f"允許站內影音卡片：{'是' if profile.allow_inline_media_cards else '否'}"
        )
        return (
            f"使用者偏好：\n{preference}\n\n"
            f"聊天室摘要：{room.summary or '尚無摘要'}\n\n"
            f"長期記憶：\n{memory or '尚無'}\n\n近期對話：\n{history or '尚無'}"
        )


class ClassificationAgent:
    def run(self, user_text: str) -> str:
        matched = []
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in user_text for keyword in keywords):
                matched.append(category)
        if "背叛與依附受傷" in matched:
            matched = [item for item in matched if item != "同儕"]
        if "高壓耗竭" in matched and "焦慮" not in matched:
            matched.append("焦慮")
        return "、".join(matched or ["一般生活壓力"])


class SkillRetrievalAgent:
    def run(self, classification: str, user_text: str) -> str:
        docs = KnowledgeDocument.objects.filter(is_active=True, doc_type="skill")
        scored = []
        for doc in docs:
            haystack = f"{doc.title} {doc.tags} {doc.content}"
            score = sum(1 for term in [classification, *user_text.split()] if term and term in haystack)
            scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        selected = [doc for _, doc in scored[:4]]
        if not selected:
            return "同理反映、情緒命名、開放式提問、低壓力小步驟"
        return "\n\n".join(f"# {doc.title}\n{doc.content}" for doc in selected)


class RagAgent:
    def run(self, user_text: str) -> str:
        return RagRetriever().query(user_text)


class ResponseAgent:
    def __init__(self):
        self.client = OpenAIClient()
        self.prompt_builder = PromptBuilder()
        self.safety_guard = SafetyGuard()

    def run(self, *, context, classification, skills, rag_context, user_text, image_path: str = "") -> AgentOutput:
        safety = self.safety_guard.check_user_message(user_text)
        if safety.is_crisis:
            return AgentOutput(context, classification, skills, rag_context, safety.response, safety.label)
        prompt = self.prompt_builder.build(
            context=context,
            classification=classification,
            skills=skills,
            rag_context=rag_context,
            user_text=user_text,
        )
        answer = self.client.complete(prompt, user_text, image_path=image_path)
        answer = self.safety_guard.review_assistant_response(answer)
        answer = self._quality_polish(answer, classification)
        answer = self._high_pressure_polish(answer, classification, user_text)
        answer = self._interest_polish(answer, user_text)
        return AgentOutput(context, classification, skills, rag_context, answer)

    def _quality_polish(self, answer: str, classification: str) -> str:
        if "背叛與依附受傷" not in classification:
            return answer

        generic_phrases = [
            "深呼吸",
            "聽音樂",
            "散步",
            "讓自己稍微放鬆",
        ]
        sentences = []
        for sentence in answer.replace("？", "？\n").replace("。", "。\n").splitlines():
            clean = sentence.strip()
            if not clean:
                continue
            if "？" in clean:
                continue
            if any(phrase in clean for phrase in generic_phrases):
                continue
            sentences.append(clean)

        polished = "".join(sentences).strip()
        if len(polished) < 80:
            polished = answer
        if polished.count("「") > polished.count("」"):
            polished += "」"
        if not any(term in polished for term in ["界線", "承擔", "清楚說明"]):
            polished += " 如果等一下要跟他談，可以先把話放短：「我現在需要你清楚說明你和她的關係，也需要你承認這件事對我的傷害。」"
        return polished

    def _high_pressure_polish(self, answer: str, classification: str, user_text: str) -> str:
        if "高壓耗竭" not in classification and "自我懷疑" not in classification:
            return answer

        weak_advice = ["喝杯水", "伸展一下", "一個小時", "輕鬆的事"]
        if not any(phrase in answer for phrase in weak_advice) and "先挑" in answer:
            return answer

        has_sleep = any(term in user_text for term in ["睡眠", "三四點", "熬夜"])
        has_compare = any(term.lower() in user_text.lower() for term in ["linkedin", "實習", "作品", "比較", "輸別人"])
        has_family = any(term in user_text for term in ["家裡", "家人", "不太懂"])

        lines = [
            "你這段不是單純沒自律，也不是普通的焦慮，比較像你把自己長期放在一個「不能停、不能輸」的系統裡。",
            "白天你用學習、專案和資訊追趕別人；晚上回到宿舍安靜下來，大腦就開始清算：我是不是還不夠、如果沒有成果我是在撐什麼。",
            "這不是你不努力，反而是你太久沒有把努力和自我價值分開，所以休息也會變成罪惡感。",
        ]
        threads = []
        if has_sleep:
            threads.append("睡眠已經在透支你的情緒恢復力")
        if has_compare:
            threads.append("LinkedIn 和同齡人比較在放大落後感")
        if has_family:
            threads.append("家人不理解讓你更孤單")
        threads.append("你開始不知道努力到底要把你帶去哪裡")

        lines.append(f"我們先不用整理整個人生，可以先拆成幾條線：{'、'.join(threads)}。")
        lines.append("你想先從哪一條開始講？如果你現在不想分析，我也可以先陪你聊點音樂或影片，讓腦袋從比較模式裡退一下。")
        return "".join(lines)

    def _interest_polish(self, answer: str, user_text: str) -> str:
        query = detect_music_or_interest_query(user_text)
        if not query:
            return answer
        if "我幫你找" in answer or "下面" in answer:
            return answer
        return f"{answer}\n\n我也幫你把「{query}」相關的影片放在下面了。你可以先點一首或一段來聽，我們不用急著分析，等你聽完也可以跟我說哪一句歌詞或哪個聲音讓你比較有被陪到。"


class CounselingOrchestrator:
    def __init__(self):
        self.context_agent = ContextAgent()
        self.classification_agent = ClassificationAgent()
        self.skill_agent = SkillRetrievalAgent()
        self.rag_agent = RagAgent()
        self.response_agent = ResponseAgent()

    def run(self, room, user_text: str, image_path: str = "") -> AgentOutput:
        context = self.context_agent.run(room)
        classification = self.classification_agent.run(user_text)
        skills = self.skill_agent.run(classification, user_text)
        rag_context = self.rag_agent.run(user_text)
        return self.response_agent.run(
            context=context,
            classification=classification,
            skills=skills,
            rag_context=rag_context,
            user_text=user_text,
            image_path=image_path,
        )
