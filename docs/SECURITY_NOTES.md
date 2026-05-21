# Security Notes

MVP 仍需維持最低安全底線：

- 密碼由 Django 內建系統雜湊，不明文保存。
- OpenAI API Key 僅存放在 `.env`。
- `.env`、SQLite DB、Markdown logs、ChromaDB index 不推上 GitHub。
- 使用者只能讀寫自己的聊天室。
- 危機風險由 `SafetyGuard` 優先攔截。
- 系統不得宣稱自己是醫師或心理師。
- 系統不得做正式診斷。
- 系統不得提供停藥、改藥或替代治療指示。
