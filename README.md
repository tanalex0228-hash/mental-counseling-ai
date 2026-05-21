# 心理諮商 LINE Bot / Web Chat 系統

這是一個以 Django、SQLite、HTML/CSS、Django REST Framework、OpenAI API、ChromaDB 建立的心理諮商陪伴聊天 MVP。介面參考 ChatGPT / Gemini，但回答流程會先讀取近期對話、聊天室摘要、心理諮商規範、技能文件、生活情境分類與 RAG 檢索結果。

## 目前架構

- `config/`：Django 專案設定。
- `accounts/`：註冊、Profile、Email、電話、主題色、密碼設定。
- `chat/`：聊天室、訊息、Markdown 備份、DRF API。
- `llm_engine/`：OpenAI client、prompt builder、RAG、safety guard、multi-agent orchestration。
- `knowledge_base/`：心理諮商規範、技能、分類、安全文件。
- `vector_store/`：ChromaDB index 建立與匯入程式。
- `docs/`：資料庫、Agent、RAG、安全與開發規則文件。
- `templates/`：登入、註冊、聊天介面。
- `static/css/app.css`：ChatGPT 類型雙欄聊天 UI 與使用者色調。
- `db.sqlite3`：本地測試資料庫，執行 migration 後產生。
- `.env`：本機密鑰與 OpenAI Token，不能推上 GitHub。

## 本地啟動

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 manage.py migrate
python3 manage.py seed_knowledge
python3 manage.py build_vector_index
python3 manage.py createsuperuser
python3 manage.py runserver 127.0.0.1:8000
```

打開 `http://127.0.0.1:8000` 後可以註冊帳號、建立對話、切換聊天紀錄與儲存色調。

Ubuntu Server 遠端測試時可使用：

```bash
python manage.py runserver 0.0.0.0:8000
```

登入後也可以用 JSON API 建立訊息：

```http
POST /api/chat/
Content-Type: application/json

{"room_id": 1, "message": "我最近壓力很大"}
```

若不傳 `room_id`，系統會自動建立一個新的聊天室。

## 資料庫設計

目前使用 SQLite 單一資料庫，但所有核心資料都用 `user` 權限隔離：

- `User`：Django 內建帳號、密碼雜湊與 Email。
- `UserProfile`：Email、電話、偏好色調。
- `ChatRoom`：每位使用者的聊天室、標題、摘要。
- `ChatMessage`：逐則保存訊息、token count、Markdown 備份路徑。
- `UserMemory`：長期記憶與諮商脈絡摘要。
- `KnowledgeDocument`：心理學文件 metadata 與內容。

正式商業化時可以改 PostgreSQL，並用租戶欄位或獨立 schema 做更強的使用者資料隔離。

## LLM 與 Multi Agent 管線

`llm_engine/agents.py` 採固定順序的可控 Multi-Agent：

1. `ContextAgent`：讀取聊天室摘要、近期對話、使用者長期記憶。
2. `ClassificationAgent`：判斷感情、家庭、學業壓力、焦慮、危機風險等分類。
3. `SkillRetrievalAgent`：查找適合的心理諮商技能。
4. `RagAgent`：從 ChromaDB 或 Markdown fallback 檢索知識庫。
5. `ResponseAgent`：組 prompt、呼叫 OpenAI、通過 safety guard。
6. Logger 流程：聊天 view 儲存 SQL，`markdown_logger` 寫入 Markdown。

若 `.env` 尚未設定 `OPENAI_API_KEY`，系統會回傳本地 fallback 訊息，方便先測 UI 與資料庫。若 OpenAI 連線失敗，也會回到 fallback，不會讓聊天流程整個壞掉。

## 心理諮商文件擴充方式

知識文件放在 `knowledge_base/`。修改 Markdown 後執行：

```bash
python manage.py seed_knowledge
python manage.py build_vector_index
```

也可以登入 Django Admin 新增 `KnowledgeDocument`：

- `policy`：模型回答規範，例如安全界線、危機處理、不可診斷。
- `skill`：心理諮商方法，例如情緒反映、開放式提問、認知重整。
- `category`：生活情境分類，例如感情、家庭、同儕、伴侶、生活壓力。

未來可以把大量論文、臨床經驗與技術文件轉成段落後放入 `knowledge_base/` 或 `knowledge_base/source_notes/`，再重建向量資料庫。

## Markdown 備份

每個聊天室會建立獨立 Markdown log：

```text
user_data/markdown_logs/{user_id}/{room_id}.md
```

`ChatMessage.markdown_backup_path` 會保存該訊息對應的備份檔案路徑。

## 五天開發建議

第 1 天：完成帳號、資料庫、聊天 UI、OpenAI 串接。

第 2 天：補管理後台、文件匯入、Markdown 匯出、基本安全設定。

第 3 天：加入 LINE Webhook、使用者綁定、訊息同步。

第 4 天：加入訂閱制、付款狀態、使用量限制、錯誤紀錄。

第 5 天：部署到伺服器、設定 HTTPS、備份、監控與正式測試。

## 重要提醒

心理諮商服務牽涉高度敏感個資。現在可以先用測試架構快速開發，但上線前至少需要 HTTPS、環境變數管理、資料庫備份、密碼重設、日誌遮罩、權限控管、使用者同意書、危機處理聲明與醫療免責說明。
