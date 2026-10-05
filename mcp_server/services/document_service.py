import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/metadata.db'))

class DocumentService:
    @staticmethod
    def get_connection():
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        # We ensure the table exists so queries won't crash on a fresh install
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                filename TEXT UNIQUE,
                file_size INTEGER,
                page_count INTEGER,
                chunk_count INTEGER,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        return conn

    @staticmethod
    def list_documents() -> list[dict]:
        """Fetch all indexed documents from SQLite"""
        conn = DocumentService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, page_count, chunk_count, file_size, uploaded_at FROM documents")
        docs = cursor.fetchall()
        conn.close()
        
        result = []
        for row in docs:
            result.append({
                "filename": row[0],
                "page_count": row[1] or 0,
                "chunk_count": row[2] or 0,
                "file_size": row[3] or 0,
                "uploaded_at": row[4] or "unknown"
            })
        return result

    @staticmethod
    def get_document_info(document_name: str) -> dict | None:
        """Fetch specific document metadata"""
        conn = DocumentService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, file_size, page_count, chunk_count, uploaded_at FROM documents WHERE filename = ?", (document_name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "filename": row[0],
                "file_size": row[1] or 0,
                "page_count": row[2] or 0,
                "chunk_count": row[3] or 0,
                "uploaded_at": row[4] or "unknown"
            }
        return None

    @staticmethod
    def search_documents(query: str) -> list[dict]:
        """Search documents by filename matching"""
        conn = DocumentService.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT filename, file_size FROM documents WHERE filename LIKE ?", (f"%{query}%",))
        docs = cursor.fetchall()
        conn.close()
        
        result = []
        for row in docs:
            result.append({
                "filename": row[0],
                "file_size": row[1] or 0
            })
        return result
