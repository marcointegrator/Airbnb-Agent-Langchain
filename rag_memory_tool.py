from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel, Field
import os

load_dotenv(Path(__file__).parent.parent / ".env")

BASE_DIR = Path(__file__).parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "oasi_sabaudia_kb"
TOP_K = 4


def _get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def _reset_chroma_client_cache() -> None:
    """Chiude i client Chroma in cache per evitare errori dopo la cancellazione del DB."""
    from chromadb.api.shared_system_client import SharedSystemClient

    for system in list(SharedSystemClient._identifier_to_system.values()):
        try:
            system.stop()
        except Exception:
            pass
    SharedSystemClient.clear_system_cache()


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )


def clear_chroma_database() -> str:
    """Cancella completamente il database Chroma locale e tutti i documenti salvati."""
    import shutil

    if not CHROMA_DIR.exists():
        return "Il database era già vuoto (cartella chroma_db non presente)."

    doc_count = 0
    try:
        doc_count = get_vector_store()._collection.count()
    except Exception:
        pass
    finally:
        _reset_chroma_client_cache()

    shutil.rmtree(CHROMA_DIR)

    if doc_count:
        return (
            f"Database cancellato: {doc_count} documenti rimossi "
            f"dalla collection '{COLLECTION_NAME}'."
        )
    return f"Database cancellato: cartella '{CHROMA_DIR.name}' rimossa."


class RagMemoryInput(BaseModel):
    query: str = Field(
        description="Domanda dell'ospite su casa, servizi, regole o zona di Sabaudia"
    )


@tool(args_schema=RagMemoryInput)
def rag_memory_tool(query: str) -> str:
    """Cerca informazioni sulla casa vacanze e sulla zona di Sabaudia nella knowledge base."""
    vector_store = get_vector_store()

    if vector_store._collection.count() == 0:
        return (
            "La knowledge base non è ancora popolata. "
            "Esegui prima: python -m tools.ingest_knowledge"
        )

    results = vector_store.similarity_search(query, k=TOP_K)
    if not results:
        return "Nessuna informazione trovata per questa richiesta."

    chunks = []
    for index, doc in enumerate(results, start=1):
        source = doc.metadata.get("source", "documento")
        chunks.append(f"[{index}] ({source})\n{doc.page_content.strip()}")

    return "\n\n---\n\n".join(chunks)
