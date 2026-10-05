import os
from langchain_community.vectorstores import Chroma
from app.rag.embeddings import get_embeddings

CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/chroma"))

def get_chroma_client():
    os.makedirs(CHROMA_PATH, exist_ok=True)
    embeddings = get_embeddings()
    return Chroma(
        collection_name="smartdocs_collection",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )
