from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db, Document
from app.rag.vector_store import get_chroma_client
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
import os
import uuid
import pymupdf as fitz

router = APIRouter()
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    results = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chroma_client = get_chroma_client()
    
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Check database
        existing_doc = db.query(Document).filter(Document.filename == file.filename).first()
        if existing_doc:
            results.append({"filename": file.filename, "error": "Document already exists"})
            continue

        # Extract text page by page using PyMuPDF
        try:
            doc = fitz.open(file_path)
            page_count = len(doc)
            text_data = []
            
            for page_num in range(page_count):
                page = doc.load_page(page_num)
                text_data.append({"page": page_num + 1, "text": page.get_text()})
            doc.close()
        except Exception as e:
            results.append({"filename": file.filename, "error": f"Failed to parse document: {str(e)}"})
            continue
        
        # Process Chunks
        chunks_stored = 0
        for data in text_data:
            chunks = text_splitter.split_text(data["text"])
            metadatas = [{"document": file.filename, "page": data["page"], "chunk_id": str(uuid.uuid4())} for _ in chunks]
            if chunks:
                chroma_client.add_texts(texts=chunks, metadatas=metadatas)
                chunks_stored += len(chunks)

        # Save Metadata to SQLite
        db_doc = Document(
            filename=file.filename,
            file_size=os.path.getsize(file_path),
            page_count=page_count,
            chunk_count=chunks_stored
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        results.append({
            "filename": file.filename, 
            "status": "success", 
            "pages": page_count, 
            "chunks": chunks_stored
        })

    return {"results": results}

@router.delete("/{filename}")
async def delete_document(filename: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.filename == filename).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete local file
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete from chroma db
    chroma_client = get_chroma_client()
    try:
        chroma_client._collection.delete(where={"document": filename})
    except Exception as e:
        print(f"Warning: failure deleting from chroma: {e}")

    # Delete from sqlite
    db.delete(doc)
    db.commit()

    return {"message": f"{filename} deleted successfully"}


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return [{"filename": d.filename, "pages": d.page_count, "chunks": d.chunk_count, "uploaded_at": d.uploaded_at} for d in docs]
