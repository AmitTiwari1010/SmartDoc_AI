import sys
import os

# Add the root directory to PYTHONPATH so imports like 'mcp_server.services' work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP
from mcp_server.tools.document_tools import register_tools

# Initialize standard AI server
mcp = FastMCP("SmartDocs MCP Server")

# Register our RAG Document tools
register_tools(mcp)

if __name__ == "__main__":
    # Start the stdio transport
    print("Starting SmartDocs MCP Server...")
    mcp.run()
