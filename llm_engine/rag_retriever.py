from pathlib import Path
import hashlib
import math

from django.conf import settings


def hash_embedding(text: str, dimensions: int = 64):
    vector = [0.0] * dimensions
    words = [word for word in text.replace("\n", " ").split(" ") if word]
    for word in words:
        digest = hashlib.sha256(word.encode("utf-8")).digest()
        index = digest[0] % dimensions
        vector[index] += 1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def chunk_text(text: str, max_chars: int = 900):
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks = []
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) > max_chars and current:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()
    if current:
        chunks.append(current)
    return chunks


class RagRetriever:
    def __init__(self):
        import chromadb

        self.client = chromadb.PersistentClient(path=str(settings.CHROMA_DB_DIR))
        self.collection = self.client.get_or_create_collection(name="counseling_knowledge")

    def query(self, text: str, n_results: int = 4) -> str:
        if self.collection.count() == 0:
            return self._fallback_file_search(text, n_results=n_results)
        results = self.collection.query(
            query_embeddings=[hash_embedding(text)],
            n_results=n_results,
        )
        documents = results.get("documents", [[]])[0]
        return "\n\n".join(documents)

    def _fallback_file_search(self, text: str, n_results: int = 4) -> str:
        query_terms = [term for term in text.lower().split() if term]
        scored = []
        for path in Path(settings.KNOWLEDGE_BASE_DIR).rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            score = sum(1 for term in query_terms if term in content.lower())
            scored.append((score, path.name, content[:1600]))
        scored.sort(reverse=True)
        return "\n\n".join(f"# {name}\n{content}" for _, name, content in scored[:n_results])
