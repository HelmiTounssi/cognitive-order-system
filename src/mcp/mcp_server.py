"""
Serveur MCP (Model Context Protocol) pour les outils
Expose les outils existants via le protocole MCP pour permettre la communication
avec des agents externes
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import des outils existants
from src.mcp.tools import (
    create_order_tool, check_stock_tool, process_payment_tool,
    update_order_status_tool, get_product_details_tool,
    get_client_details_tool, validate_order_tool, recommend_products_tool,
    get_order_history_tool, add_client_tool, list_clients_tool,
    introspect_ontology_tool, extend_ontology_tool, create_instance_tool,
    query_ontology_tool, get_all_orders_tool, add_behavior_class_tool,
    add_state_machine_tool, execute_behavior_tool, create_semantic_proxy_tool,
    execute_method_reflection_tool, reflect_class_tool,
    instantiate_by_reflection_tool, list_proxy_methods_tool
)
from src.core.knowledge_base import KnowledgeBase
from src.rag.vector_store import VectorStore

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServer:
    """
    Serveur MCP qui expose les outils via le protocole MCP
    """
    
    def __init__(self, knowledge_base: KnowledgeBase, vector_store: VectorStore):
        """
        Initialise le serveur MCP
        
        Args:
            knowledge_base: Instance de la base de connaissances
            vector_store: Instance de la base vectorielle
        """
        self.kb = knowledge_base
        self.vector_store = vector_store
        self.clients = {}
        self.tool_registry = self._register_tools()
        
    def _register_tools(self) -> Dict[str, Dict]:
        """
        Enregistre tous les outils disponibles
        
        Returns:
            Dict: Registre des outils avec leurs métadonnées
        """
        return {
            "create_order": {
                "name": "create_order",
                "description": "Crée une nouvelle commande pour un client",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "ID du client"},
                        "items_list": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "product_id": {"type": "string"},
                                    "quantity": {"type": "integer"}
                                }
                            }
                        }
                    },
                    "required": ["client_id", "items_list"]
                },
                "function": create_order_tool
            },
            "check_stock": {
                "name": "check_stock",
                "description": "Vérifie la disponibilité en stock d'un produit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "ID du produit"},
                        "quantity": {"type": "integer", "description": "Quantité demandée"}
                    },
                    "required": ["product_id", "quantity"]
                },
                "function": check_stock_tool
            },
            "process_payment": {
                "name": "process_payment",
                "description": "Traite le paiement d'une commande",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "ID de la commande"},
                        "amount": {"type": "number", "description": "Montant à payer"}
                    },
                    "required": ["order_id", "amount"]
                },
                "function": process_payment_tool
            },
            "validate_order": {
                "name": "validate_order",
                "description": "Valide une commande",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string", "description": "ID de la commande"}
                    },
                    "required": ["order_id"]
                },
                "function": validate_order_tool
            },
            "get_product_details": {
                "name": "get_product_details",
                "description": "Récupère les détails d'un produit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "ID du produit"}
                    },
                    "required": ["product_id"]
                },
                "function": get_product_details_tool
            },
            "get_client_details": {
                "name": "get_client_details",
                "description": "Récupère les détails d'un client",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string", "description": "ID du client"}
                    },
                    "required": ["client_id"]
                },
                "function": get_client_details_tool
            },
            "recommend_products": {
                "name": "recommend_products",
                "description": "Recommande des produits basés sur une requête",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {"type": "string", "description": "Requête de recherche"},
                        "top_k": {"type": "integer", "description": "Nombre de recommandations", "default": 3}
                    },
                    "required": ["query_text"]
                },
                "function": recommend_products_tool
            },
            "add_client": {
                "name": "add_client",
                "description": "Ajoute un nouveau client",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Nom du client"},
                        "email": {"type": "string", "description": "Email du client"}
                    },
                    "required": ["name", "email"]
                },
                "function": add_client_tool
            },
            "list_clients": {
                "name": "list_clients",
                "description": "Liste tous les clients",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "function": list_clients_tool
            },
            "introspect_ontology": {
                "name": "introspect_ontology",
                "description": "Analyse la structure de l'ontologie",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "function": introspect_ontology_tool
            },
            "extend_ontology": {
                "name": "extend_ontology",
                "description": "Étend l'ontologie avec une nouvelle classe",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Nom de la classe"},
                        "properties": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string"}
                                }
                            }
                        },
                        "namespace": {"type": "string", "description": "Namespace (optionnel)"}
                    },
                    "required": ["class_name", "properties"]
                },
                "function": extend_ontology_tool
            },
            "create_instance": {
                "name": "create_instance",
                "description": "Crée une nouvelle instance d'une classe",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Nom de la classe"},
                        "properties": {"type": "object", "description": "Propriétés de l'instance"},
                        "instance_id": {"type": "string", "description": "ID de l'instance (optionnel)"}
                    },
                    "required": ["class_name", "properties"]
                },
                "function": create_instance_tool
            },
            "query_ontology": {
                "name": "query_ontology",
                "description": "Requête l'ontologie",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {"type": "string", "description": "Type de requête"},
                        "kwargs": {"type": "object", "description": "Paramètres supplémentaires"}
                    },
                    "required": ["query_type"]
                },
                "function": query_ontology_tool
            },
            "get_all_orders": {
                "name": "get_all_orders",
                "description": "Récupère toutes les commandes",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "function": get_all_orders_tool
            },
            "add_behavior_class": {
                "name": "add_behavior_class",
                "description": "Ajoute une classe avec des comportements",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Nom de la classe"},
                        "methods": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "parameters": {"type": "array"},
                                    "body": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["class_name", "methods"]
                },
                "function": add_behavior_class_tool
            },
            "add_state_machine": {
                "name": "add_state_machine",
                "description": "Ajoute une machine à états",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Nom de la classe"},
                        "states": {"type": "array", "items": {"type": "string"}},
                        "transitions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "from_state": {"type": "string"},
                                    "to_state": {"type": "string"},
                                    "condition": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["class_name", "states", "transitions"]
                },
                "function": add_state_machine_tool
            },
            "execute_behavior": {
                "name": "execute_behavior",
                "description": "Exécute un comportement sur une instance",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string", "description": "ID de l'instance"},
                        "method_name": {"type": "string", "description": "Nom de la méthode"},
                        "parameters": {"type": "object", "description": "Paramètres de la méthode"}
                    },
                    "required": ["instance_id", "method_name"]
                },
                "function": execute_behavior_tool
            },
            "create_semantic_proxy": {
                "name": "create_semantic_proxy",
                "description": "Crée un proxy sémantique pour une classe",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Nom de la classe"},
                        "instance_id": {"type": "string", "description": "ID de l'instance (optionnel)"}
                    },
                    "required": ["class_name"]
                },
                "function": create_semantic_proxy_tool
            },
            "execute_method_reflection": {
                "name": "execute_method_reflection",
                "description": "Exécute une méthode via réflexion",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "proxy_id": {"type": "string", "description": "ID du proxy"},
                        "method_name": {"type": "string", "description": "Nom de la méthode"},
                        "parameters": {"type": "object", "description": "Paramètres"}
                    },
                    "required": ["proxy_id", "method_name"]
                },
                "function": execute_method_reflection_tool
            },
            "reflect_class": {
                "name": "reflect_class",
                "description": "Analyse une classe via réflexion",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Nom de la classe"}
                    },
                    "required": ["class_name"]
                },
                "function": reflect_class_tool
            },
            "instantiate_by_reflection": {
                "name": "instantiate_by_reflection",
                "description": "Instancie une classe via réflexion",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Nom de la classe"},
                        "properties": {"type": "object", "description": "Propriétés"}
                    },
                    "required": ["class_name", "properties"]
                },
                "function": instantiate_by_reflection_tool
            },
            "list_proxy_methods": {
                "name": "list_proxy_methods",
                "description": "Liste les méthodes disponibles d'un proxy",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string", "description": "Nom de la classe"}
                    },
                    "required": ["class_name"]
                },
                "function": list_proxy_methods_tool
            }
        }
    
    async def handle_mcp_request(self, request: Dict) -> Dict:
        """
        Gère une requête MCP
        
        Args:
            request: Requête MCP
        
        Returns:
            Dict: Réponse MCP
        """
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
        """
        Gère l'initialisation du client MCP
        
        Args:
            request_id: ID de la requête
            params: Paramètres d'initialisation
        
        Returns:
            Dict: Réponse d'initialisation
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "CognitiveOrderAgent MCP Server",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_list_tools(self, request_id: str) -> Dict:
        """
        Liste tous les outils disponibles
        
        Args:
            request_id: ID de la requête
        
        Returns:
            Dict: Liste des outils
        """
        tools = []
        for tool_id, tool_info in self.tool_registry.items():
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
        """
        Appelle un outil spécifique
        
        Args:
            request_id: ID de la requête
            params: Paramètres de l'appel
        
        Returns:
            Dict: Résultat de l'appel
        """
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tool_registry:
            return self._create_error_response(request_id, "Tool not found", f"Tool {tool_name} not found")
        
        try:
            tool_info = self.tool_registry[tool_name]
            tool_function = tool_info["function"]
            
            # Ajoute les dépendances nécessaires aux arguments
            if tool_name in ["create_order", "check_stock", "process_payment", "update_order_status", 
                           "get_product_details", "get_client_details", "validate_order", 
                           "get_order_history", "add_client", "list_clients", "introspect_ontology",
                           "extend_ontology", "create_instance", "query_ontology", "get_all_orders",
                           "add_behavior_class", "add_state_machine", "execute_behavior",
                           "create_semantic_proxy", "execute_method_reflection", "reflect_class",
                           "instantiate_by_reflection", "list_proxy_methods"]:
                arguments["knowledge_base"] = self.kb
            
            if tool_name in ["recommend_products"]:
                arguments["knowledge_base"] = self.kb
                arguments["vector_store"] = self.vector_store
            
            # Ajoute des valeurs par défaut pour les outils qui en ont besoin
            if tool_name == "add_state_machine":
                arguments.setdefault("class_name", "DefaultClass")
                arguments.setdefault("states", ["initial", "final"])
                arguments.setdefault("transitions", [])
            elif tool_name == "create_order":
                arguments.setdefault("client_id", "default_client")
                arguments.setdefault("items_list", [])
            elif tool_name == "add_behavior_class":
                arguments.setdefault("class_name", "DefaultBehavior")
                arguments.setdefault("methods", [])
            elif tool_name == "create_instance":
                arguments.setdefault("class_name", "DefaultClass")
                arguments.setdefault("properties", {})
            elif tool_name == "extend_ontology":
                arguments.setdefault("class_name", "NewClass")
                arguments.setdefault("properties", [])
            
            # Exécute l'outil
            result = tool_function(**arguments)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'outil {tool_name}: {e}")
            return self._create_error_response(request_id, "Tool execution error", str(e))
    
    def _create_error_response(self, request_id: str, code: str, message: str) -> Dict:
        """
        Crée une réponse d'erreur MCP
        
        Args:
            request_id: ID de la requête
            code: Code d'erreur
            message: Message d'erreur
        
        Returns:
            Dict: Réponse d'erreur
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601 if code == "Method not found" else -32603,
                "message": code,
                "data": message
            }
        }


class MCPServerManager:
    """
    Gestionnaire du serveur MCP
    """
    
    def __init__(self, knowledge_base: KnowledgeBase, vector_store: VectorStore):
        """
        Initialise le gestionnaire
        
        Args:
            knowledge_base: Instance de la base de connaissances
            vector_store: Instance de la base vectorielle
        """
        self.mcp_server = MCPServer(knowledge_base, vector_store)
        self.server_task = None
    
    async def start_server(self, host: str = "localhost", port: int = 8001):
        """
        Démarre le serveur MCP
        
        Args:
            host: Adresse d'écoute
            port: Port d'écoute
        """
        try:
            # Crée le serveur WebSocket
            import websockets
            
            async def handle_websocket(websocket):
                """Gère les connexions WebSocket"""
                client_id = str(uuid.uuid4())
                self.mcp_server.clients[client_id] = websocket
                
                logger.info(f"Client MCP connecté: {client_id}")
                
                try:
                    async for message in websocket:
                        try:
                            request = json.loads(message)
                            response = await self.mcp_server.handle_mcp_request(request)
                            await websocket.send(json.dumps(response))
                        except json.JSONDecodeError:
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
                except websockets.exceptions.ConnectionClosed:
                    logger.info(f"Client MCP déconnecté: {client_id}")
                finally:
                    if client_id in self.mcp_server.clients:
                        del self.mcp_server.clients[client_id]
            
            # Démarre le serveur
            server = await websockets.serve(handle_websocket, host, port)
            logger.info(f"Serveur MCP démarré sur ws://{host}:{port}")
            
            # Garde le serveur en vie
            await server.wait_closed()
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du serveur MCP: {e}")
    
    def stop_server(self):
        """
        Arrête le serveur MCP
        """
        if self.server_task and not self.server_task.done():
            self.server_task.cancel()
            logger.info("Serveur MCP arrêté")


# Fonction utilitaire pour démarrer le serveur MCP
async def start_mcp_server(knowledge_base: KnowledgeBase, vector_store: VectorStore, 
                          host: str = "localhost", port: int = 8001):
    """
    Démarre le serveur MCP
    
    Args:
        knowledge_base: Instance de la base de connaissances
        vector_store: Instance de la base vectorielle
        host: Adresse d'écoute
        port: Port d'écoute
    """
    manager = MCPServerManager(knowledge_base, vector_store)
    await manager.start_server(host, port)


if __name__ == "__main__":
    # Test du serveur MCP
    import asyncio
    
    async def test_mcp_server():
        # Crée des instances mock pour le test
        kb = KnowledgeBase()
        vs = VectorStore()
        
        # Démarre le serveur
        await start_mcp_server(kb, vs)
    
    asyncio.run(test_mcp_server()) 