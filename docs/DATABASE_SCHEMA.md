# Database Schema

## User

Django 內建 `auth.User` 負責帳號、密碼雜湊、Email。

## UserProfile

位於 `accounts.UserProfile`：

- `user`
- `email`
- `phone_number`
- `preferred_theme_color`
- `created_at`
- `updated_at`

## ChatRoom

位於 `chat.ChatRoom`：

- `user`
- `title`
- `summary`
- `created_at`
- `updated_at`

## ChatMessage

位於 `chat.ChatMessage`：

- `room`
- `user`
- `role`
- `content`
- `created_at`
- `markdown_backup_path`
- `token_count`

## UserMemory

位於 `chat.UserMemory`：

- `user`
- `memory_type`
- `content`
- `importance_score`
- `created_at`
- `updated_at`

## KnowledgeDocument

位於 `chat.KnowledgeDocument`：

- `title`
- `doc_type`
- `category`
- `source_type`
- `file_path`
- `vector_index_id`
- `content`
- `created_at`
- `updated_at`
