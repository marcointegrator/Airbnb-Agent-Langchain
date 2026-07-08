from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from tools.rag_memory_tool import CHROMA_DIR, COLLECTION_NAME, clear_chroma_database, get_vector_store

load_dotenv(Path(__file__).parent.parent / ".env")

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"


def load_documents():
    docs = []
    for path in sorted(DATA_DIR.glob("**/*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        loader = TextLoader(str(path), encoding="utf-8")
        docs.extend(loader.load())
    return docs


def ingest():
    docs = load_documents()
    if not docs:
        raise FileNotFoundError(f"Nessun file .md o .txt trovato in {DATA_DIR}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(docs)

    clear_chroma_database()

    vector_store = get_vector_store()
    vector_store.add_documents(splits)

    print(f"Ingest completato: {len(splits)} chunk in '{COLLECTION_NAME}'")
    print(f"Database salvato in: {CHROMA_DIR}")


if __name__ == "__main__":
    ingest()
