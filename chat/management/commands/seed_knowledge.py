from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from chat.models import KnowledgeDocument


SEEDS = [
    {
        "title": "基礎回答規範",
        "doc_type": "policy",
        "tags": "安全,陪伴,非診斷,危機",
        "content": (
            "回答必須先承接使用者感受，再用開放式問題協助釐清。"
            "不得做臨床診斷、不得宣稱治療效果、不得鼓勵停止既有醫療。"
            "若出現自傷、傷人、家暴、急性恐慌或醫療危急，需建議立即尋求真人與緊急資源。"
        ),
    },
    {
        "title": "情緒命名與反映",
        "doc_type": "skill",
        "tags": "情緒,反映,同理",
        "content": (
            "用簡短語句反映情緒，例如：聽起來你一方面很累，另一方面也很希望事情能變好。"
            "避免急著給結論，先讓使用者感到被理解。"
        ),
    },
    {
        "title": "生活壓力分類",
        "doc_type": "category",
        "tags": "壓力,工作,課業,生活",
        "content": (
            "常見生活壓力可先拆成壓力來源、可控制因素、不可控制因素、今天能做的小行動。"
            "回應時要把建議縮小到可執行的一步。"
        ),
    },
    {
        "title": "關係與伴侶分類",
        "doc_type": "category",
        "tags": "感情,伴侶,家庭,同儕",
        "content": (
            "關係議題先確認使用者在關係中的感受、界線、期待與溝通困難。"
            "建議可包含非暴力溝通、界線表達、暫停衝突升溫。"
        ),
    },
]

FILE_DOC_TYPES = {
    "counseling_response_policy.md": ("policy", "回答規範"),
    "counseling_skills.md": ("skill", "諮商技能"),
    "life_situation_taxonomy.md": ("category", "生活情境分類"),
    "clinical_guardrails.md": ("guardrail", "臨床安全規則"),
}


class Command(BaseCommand):
    help = "Seed starter counseling knowledge documents."

    def handle(self, *args, **options):
        created = 0
        for seed in SEEDS:
            _, was_created = KnowledgeDocument.objects.update_or_create(
                title=seed["title"],
                defaults=seed,
            )
            created += int(was_created)
        for path in Path(settings.KNOWLEDGE_BASE_DIR).rglob("*.md"):
            doc_type, category = FILE_DOC_TYPES.get(path.name, ("source_note", "來源筆記"))
            _, was_created = KnowledgeDocument.objects.update_or_create(
                file_path=str(path),
                defaults={
                    "title": path.stem.replace("_", " ").title(),
                    "doc_type": doc_type,
                    "category": category,
                    "source_type": "markdown",
                    "tags": category,
                    "content": path.read_text(encoding="utf-8"),
                    "is_active": True,
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"Knowledge documents ready. Created: {created}"))
