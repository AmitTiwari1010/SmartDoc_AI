try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP
from mcp_server.services.document_service import DocumentService

def register_tools(mcp: FastMCP):
    
    @mcp.tool()
    def list_documents() -> str:
        """List all indexed documents in the knowledge base"""
        docs = DocumentService.list_documents()
        if not docs:
            return "No documents found in knowledge base."
        
        return "Indexed Documents:\n" + "\n".join(
            f"- {d['filename']} (Pages: {d['page_count']}, Chunks: {d['chunk_count']})" for d in docs
        )

    @mcp.tool()
    def get_document_info(document_name: str) -> str:
        """Get metadata details for a specifically named document."""
        doc = DocumentService.get_document_info(document_name)
        if doc:
            return (f"Document Info for '{document_name}':\n"
                    f"Size: {doc['file_size']} bytes\n"
                    f"Pages: {doc['page_count']}\n"
                    f"Chunks: {doc['chunk_count']}\n"
                    f"Uploaded: {doc['uploaded_at']}")
        return f"Document '{document_name}' not found."

    @mcp.tool()
    def search_documents(query: str) -> str:
        """Find documents relevant to a keyword/query based on metadata."""
        docs = DocumentService.search_documents(query)
        if not docs:
            return f"No documents matched the query: '{query}'"
        
        return f"Search results for '{query}':\n" + "\n".join(
            f"- {d['filename']} (Size: {d['file_size']} bytes)" for d in docs
        )
