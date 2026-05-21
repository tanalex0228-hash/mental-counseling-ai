# Development Rules

- 先建立最小可執行版本，再逐步擴充。
- 指令失敗不可跳過，必須修正後繼續。
- migration 失敗要修正 model 或 migration。
- import error 要修正 requirements 或程式引用。
- API Key 只能放在 `.env`。
- 不把 `.env`、`db.sqlite3`、`user_data/`、`vector_store/chroma_db/` 推上 GitHub。
- 每完成重要功能就執行 `python manage.py check` 與測試。
