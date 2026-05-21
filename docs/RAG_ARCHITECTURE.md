# RAG Architecture

知識文件放在 `knowledge_base/`，目前包含：

- `counseling_response_policy.md`
- `counseling_skills.md`
- `life_situation_taxonomy.md`
- `clinical_guardrails.md`

重建向量資料庫：

```bash
python manage.py build_vector_index
```

向量資料庫位置：

```text
vector_store/chroma_db/
```

目前使用本地 hash embedding，優點是不需要 API Key 就可以建立 MVP。未來可以替換成 OpenAI embedding 或其他 embedding model。
