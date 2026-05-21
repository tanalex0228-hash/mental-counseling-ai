from llm_engine.agents import CounselingOrchestrator


class CounselingEngine:
    def reply(self, room, user_text: str) -> str:
        return CounselingOrchestrator().run(room, user_text).answer
