from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.vector_store import get_chroma_client
from google import genai
import os
from dotenv import load_dotenv

# Ensure .env is loaded regardless of current working directory
_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(_env_path)
load_dotenv()

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/")
def chat_endpoint(request: ChatRequest):
    chroma_client = get_chroma_client()
    
    # Semantic Search inside Vector DB
    results = chroma_client.similarity_search(request.question, k=6)
    
    seen_sources = set()
    sources = []
    context_chunks = []
    for r in results:
        context_chunks.append(r.page_content.strip())
        doc_name = r.metadata.get("document", "Unknown")
        page_num = r.metadata.get("page", 0)
        source_key = (doc_name, page_num)
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({
                "document": doc_name,
                "page": page_num,
                "chunk_id": r.metadata.get("chunk_id", "")
            })

    context = "\n\n".join(context_chunks)

    prompt = f"""You are SmartDocs AI, an intelligent, articulate document knowledge assistant powered by Google Gemini.

Provide a comprehensive, well-structured, and clear answer based on the provided document context.

Guidelines:
- Tone & Persona: Respond like Google Gemini—informative, structured, natural, and helpful.
- Direct & Engaging: Explain the concept directly and thoroughly. Do NOT start with robotic meta-disclaimers like 'Based on the provided context...' or 'The document does not explicitly define...'. Synthesize the knowledge smoothly and explain the concepts intuitively.
- Formatting:
  * Use a clean introductory overview.
  * Use structured bullet points (- or *) with **bold** key terms.
  * Use inline code formatting (e.g. `public`, `private`) where appropriate.
  * Keep paragraphs and lists clean and readable with proper markdown spacing.
- Grounding: Base your factual explanation on the provided document excerpts. If a specific detail is completely missing, mention that gracefully at the end.

DOCUMENT CONTEXT:
\"\"\"
{context}
\"\"\"

USER QUESTION:
{request.question}
"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set correctly in the environment.")
        
    models_to_try = [os.getenv("GEMINI_MODEL", "gemini-3.8-flash"), "gemini-3.5-flash-lite"]
    client = genai.Client(api_key=api_key)
    answer = None
    last_error = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            answer = response.text
            if answer:
                break
        except Exception as e:
            last_error = e
            continue

    if not answer:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(last_error)}")
    
    return {
        "answer": answer,
        "sources": sources
    }
