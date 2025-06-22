"""
Module MCP (Model Context Protocol)
Gère le serveur et client MCP, ainsi que les outils exposés
"""

from .mcp_server import MCPServer, MCPServerManager, start_mcp_server
from .mcp_client import MCPClient, MCPToolInterface
from .tools import *

__all__ = [
    'MCPServer', 
    'MCPServerManager', 
    'start_mcp_server',
    'MCPClient', 
    'MCPToolInterface'
] 