from pathlib import Path

from django.conf import settings

from llm_engine.rag_retriever import chunk_text, hash_embedding


def ingest_knowledge_base():
    import chromadb

    client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_DIR))
    try:
        client.delete_collection("counseling_knowledge")
    except Exception:
        pass
    collection = client.get_or_create_collection(name="counseling_knowledge")

    ids = []
    documents = []
    metadatas = []
    embeddings = []
    for path in Path(settings.KNOWLEDGE_BASE_DIR).rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        for index, chunk in enumerate(chunk_text(content)):
            chunk_id = f"{path.stem}-{index}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({"file_path": str(path), "source": path.name})
            embeddings.append(hash_embedding(chunk))

    if documents:
        collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    return len(documents)
