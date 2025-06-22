"""
Serveur MCP simplifié pour éviter les problèmes de signature WebSocket
"""

import asyncio
import json
import logging
import uuid
from typing import Dict
import websockets

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleMCPServer:
    """
    Serveur MCP simplifié
    """
    
    def __init__(self):
        self.clients = {}
        self.tools = {
            "list_clients": {
                "name": "list_clients",
                "description": "Liste tous les clients",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            "introspect_ontology": {
                "name": "introspect_ontology",
                "description": "Analyse la structure de l'ontologie",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            "get_all_orders": {
                "name": "get_all_orders",
                "description": "Récupère toutes les commandes",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    
    async def handle_mcp_request(self, request: Dict) -> Dict:
        """Gère une requête MCP"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            logger.info(f"Requête MCP reçue: {method}")
            
            if method == "tools/list":
                return self._handle_list_tools(request_id)
            elif method == "tools/call":
                return await self._handle_call_tool(request_id, params)
            elif method == "initialize":
                return self._handle_initialize(request_id, params)
            else:
                return self._create_error_response(request_id, "Method not found", f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la requête MCP: {e}")
            return self._create_error_response(request.get("id"), "Internal error", str(e))
    
    def _handle_initialize(self, request_id: str, params: Dict) -> Dict:
        """Gère l'initialisation"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "Simple MCP Server",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_list_tools(self, request_id: str) -> Dict:
        """Liste les outils"""
        tools = []
        for tool_id, tool_info in self.tools.items():
            tools.append({
                "name": tool_info["name"],
                "description": tool_info["description"],
                "inputSchema": tool_info["parameters"]
            })
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_call_tool(self, request_id: str, params: Dict) -> Dict:
        """Appelle un outil"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return self._create_error_response(request_id, "Tool not found", f"Tool {tool_name} not found")
        
        try:
            # Simulation des résultats
            if tool_name == "list_clients":
                result = "📋 Aucun client trouvé dans la base de données."
            elif tool_name == "introspect_ontology":
                result = "🔍 Structure de l'ontologie analysée avec succès."
            elif tool_name == "get_all_orders":
                result = "📦 Aucune commande trouvée dans le système."
            else:
                result = f"✅ Outil {tool_name} exécuté avec succès."
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'outil {tool_name}: {e}")
            return self._create_error_response(request_id, "Tool execution error", str(e))
    
    def _create_error_response(self, request_id: str, code: str, message: str) -> Dict:
        """Crée une réponse d'erreur"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601 if code == "Method not found" else -32603,
                "message": code,
                "data": message
            }
        }


async def start_simple_mcp_server(host: str = "localhost", port: int = 8001):
    """Démarre le serveur MCP simplifié"""
    server = SimpleMCPServer()
    
    async def handler(websocket):
        """Handler WebSocket simplifié"""
        client_id = str(uuid.uuid4())
        server.clients[client_id] = websocket
        
        logger.info(f"Client MCP connecté: {client_id}")
        
        try:
            async for message in websocket:
                try:
                    logger.info(f"Message reçu: {message}")
                    request = json.loads(message)
                    response = await server.handle_mcp_request(request)
                    response_str = json.dumps(response)
                    logger.info(f"Envoi réponse: {response_str}")
                    await websocket.send(response_str)
                except json.JSONDecodeError as e:
                    logger.error(f"Erreur JSON: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error",
                            "data": "Invalid JSON"
                        }
                    }
                    await websocket.send(json.dumps(error_response))
                except Exception as e:
                    logger.error(f"Erreur dans le handler: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": "Internal error",
                            "data": str(e)
                        }
                    }
                    await websocket.send(json.dumps(error_response))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client MCP déconnecté: {client_id}")
        except Exception as e:
            logger.error(f"Erreur de connexion: {e}")
        finally:
            if client_id in server.clients:
                del server.clients[client_id]
    
    # Démarre le serveur (compatible websockets 15.x)
    server_ws = await websockets.serve(handler, host, port)
    logger.info(f"Serveur MCP simplifié démarré sur ws://{host}:{port}")
    
    # Garde le serveur en vie
    await server_ws.wait_closed()


if __name__ == "__main__":
    asyncio.run(start_simple_mcp_server()) 