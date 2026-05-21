from django.core.management.base import BaseCommand

from vector_store.ingest_documents import ingest_knowledge_base


class Command(BaseCommand):
    help = "Build local ChromaDB index from knowledge_base Markdown files."

    def handle(self, *args, **options):
        count = ingest_knowledge_base()
        self.stdout.write(self.style.SUCCESS(f"Indexed {count} knowledge chunks."))
