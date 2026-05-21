# Agent Architecture

本系統採用固定順序的可控 Multi-Agent，不讓 Agent 自由決策流程。

1. `ContextAgent`：讀取聊天室摘要、近期對話、使用者長期記憶。
2. `ClassificationAgent`：判斷生活情境分類。
3. `SkillRetrievalAgent`：依分類選擇諮商技能。
4. `RagAgent`：從 ChromaDB 或 Markdown fallback 檢索知識庫。
5. `ResponseAgent`：組 prompt、呼叫 OpenAI、執行安全檢查。
6. Logger 流程：由 chat view 寫入 SQL，並透過 `markdown_logger` 寫入 Markdown 備份。
