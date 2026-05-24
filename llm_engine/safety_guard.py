from dataclasses import dataclass

from .response_policy import CRISIS_RESPONSE


CRISIS_KEYWORDS = [
    "自殺",
    "想死",
    "不想活",
    "傷害自己",
    "割腕",
    "跳樓",
    "殺了",
    "傷害他人",
    "家暴",
    "被打",
    "性侵",
    "虐待",
    "停藥",
    "改藥",
]

CRISIS_RESPONSE_MARKERS = [
    "我很在意你現在的安全",
    "若你此刻可能傷害自己",
    "立刻聯絡當地緊急服務",
    "離開可能造成傷害的物品或場所",
]


@dataclass
class SafetyResult:
    is_crisis: bool
    response: str = ""
    label: str = "normal"


class SafetyGuard:
    def check_user_message(self, text: str) -> SafetyResult:
        normalized = text.lower()
        for keyword in CRISIS_KEYWORDS:
            if keyword in normalized:
                return SafetyResult(is_crisis=True, response=CRISIS_RESPONSE, label="crisis_risk")
        return SafetyResult(is_crisis=False)

    def looks_like_crisis_response(self, text: str) -> bool:
        return any(marker in text for marker in CRISIS_RESPONSE_MARKERS)

    def review_assistant_response(self, text: str) -> str:
        blocked_claims = ["我診斷", "你得了", "停藥", "改藥"]
        if any(claim in text for claim in blocked_claims):
            return (
                "我不能做診斷或提供用藥指示。比較穩妥的方式是把你正在經歷的狀態整理出來，"
                "並在需要時和心理師、醫師或可信任的真人討論。"
            )
        return text
