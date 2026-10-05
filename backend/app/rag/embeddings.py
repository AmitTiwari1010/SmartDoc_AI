from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

def get_embeddings():
    """Uses a local MiniLM model to embed without needing OpenAI keys"""
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
