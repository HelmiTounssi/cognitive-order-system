"""
Client MCP (Model Context Protocol) pour l'agent
Permet à l'agent de communiquer avec le serveur MCP pour utiliser les outils
"""

import asyncio
import json
import logging
from typing import Dict, List, Any
import websockets

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client MCP pour communiquer avec le serveur MCP
    """
    
    def __init__(self, server_url: str = "ws://localhost:8001"):
        """
        Initialise le client MCP
        
        Args:
            server_url: URL du serveur MCP
        """
        self.server_url = server_url
        self.websocket = None
        self.connected = False
        self.request_id = 0
        self.tools_cache = None
    
    async def connect(self):
        """
        Se connecte au serveur MCP
        """
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            logger.info(f"Connecté au serveur MCP: {self.server_url}")
            
            # Initialise la connexion
            await self._initialize()
            
        except Exception as e:
            logger.error(f"Erreur de connexion au serveur MCP: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """
        Se déconnecte du serveur MCP
        """
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Déconnecté du serveur MCP")
    
    async def _initialize(self):
        """
        Initialise la connexion MCP
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "CognitiveOrderAgent",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_request(request)
        logger.info("Connexion MCP initialisée")
        return response
    
    async def list_tools(self) -> List[Dict]:
        """
        Liste tous les outils disponibles
        
        Returns:
            List[Dict]: Liste des outils
        """
        if self.tools_cache:
            return self.tools_cache
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/list",
            "params": {}
        }
        
        response = await self._send_request(request)
        
        if "result" in response and "tools" in response["result"]:
            self.tools_cache = response["result"]["tools"]
            return self.tools_cache
        else:
            logger.error("Erreur lors de la récupération des outils")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """
        Appelle un outil spécifique
        
        Args:
            tool_name: Nom de l'outil
            arguments: Arguments de l'outil
        
        Returns:
            Any: Résultat de l'appel
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if "result" in response and "content" in response["result"]:
            # Extrait le texte de la réponse
            content = response["result"]["content"]
            if content and len(content) > 0:
                return content[0].get("text", "")
            return ""
        elif "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            logger.error(f"Erreur lors de l'appel de l'outil {tool_name}: "
                        f"{error_msg}")
            raise Exception(f"Tool call error: {error_msg}")
        else:
            logger.error(f"Réponse inattendue pour l'outil {tool_name}")
            return None
    
    async def _send_request(self, request: Dict) -> Dict:
        """
        Envoie une requête au serveur MCP
        
        Args:
            request: Requête à envoyer
        
        Returns:
            Dict: Réponse du serveur
        """
        if not self.connected or not self.websocket:
            raise Exception("Client MCP non connecté")
        
        try:
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la requête MCP: {e}")
            raise
    
    def _get_next_id(self) -> str:
        """
        Génère un ID unique pour les requêtes
        
        Returns:
            str: ID unique
        """
        self.request_id += 1
        return str(self.request_id)
    
    async def __aenter__(self):
        """
        Context manager entry
        """
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit
        """
        await self.disconnect()


class MCPToolInterface:
    """
    Interface pour utiliser les outils MCP de manière synchrone
    """
    
    def __init__(self, server_url: str = "ws://localhost:8001"):
        """
        Initialise l'interface
        
        Args:
            server_url: URL du serveur MCP
        """
        self.server_url = server_url
        self.client = None
        self._loop = None
    
    def _ensure_loop(self):
        """
        S'assure qu'une boucle d'événements est disponible
        """
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            # Crée une nouvelle boucle si aucune n'est en cours
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
    
    def connect(self):
        """
        Se connecte au serveur MCP (synchrone)
        """
        self._ensure_loop()
        
        if self._loop and self._loop.is_running():
            # Si une boucle est en cours, utilise asyncio.create_task
            future = asyncio.create_task(self._connect_async())
            # Attend la fin de la tâche
            while not future.done():
                pass
            if future.exception():
                raise future.exception()
        else:
            # Sinon, exécute directement
            if self._loop:
                self._loop.run_until_complete(self._connect_async())
    
    async def _connect_async(self):
        """
        Connexion asynchrone
        """
        self.client = MCPClient(self.server_url)
        await self.client.connect()
    
    def disconnect(self):
        """
        Se déconnecte du serveur MCP (synchrone)
        """
        if self.client:
            if self._loop and self._loop.is_running():
                future = asyncio.create_task(self.client.disconnect())
                while not future.done():
                    pass
            else:
                if self._loop:
                    self._loop.run_until_complete(self.client.disconnect())
    
    def list_tools(self) -> List[Dict]:
        """
        Liste tous les outils disponibles (synchrone)
        
        Returns:
            List[Dict]: Liste des outils
        """
        if not self.client:
            raise Exception("Client MCP non connecté")
        
        if self._loop and self._loop.is_running():
            future = asyncio.create_task(self.client.list_tools())
            while not future.done():
                pass
            if future.exception():
                raise future.exception()
            return future.result()
        else:
            if self._loop:
                return self._loop.run_until_complete(self.client.list_tools())
            return []
    
    def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """
        Appelle un outil spécifique (synchrone)
        
        Args:
            tool_name: Nom de l'outil
            arguments: Arguments de l'outil
        
        Returns:
            Any: Résultat de l'appel
        """
        if not self.client:
            raise Exception("Client MCP non connecté")
        
        if self._loop and self._loop.is_running():
            future = asyncio.create_task(
                self.client.call_tool(tool_name, arguments)
            )
            while not future.done():
                pass
            if future.exception():
                raise future.exception()
            return future.result()
        else:
            if self._loop:
                return self._loop.run_until_complete(
                    self.client.call_tool(tool_name, arguments)
                )
            return None


# Fonction utilitaire pour créer une interface MCP
def create_mcp_interface(server_url: str = "ws://localhost:8001") -> MCPToolInterface:
    """
    Crée une interface MCP
    
    Args:
        server_url: URL du serveur MCP
    
    Returns:
        MCPToolInterface: Interface MCP
    """
    return MCPToolInterface(server_url)


if __name__ == "__main__":
    # Test du client MCP
    async def test_mcp_client():
        async with MCPClient() as client:
            # Liste les outils
            tools = await client.list_tools()
            print(f"Outils disponibles: {len(tools)}")
            
            for tool in tools:
                print(f"- {tool['name']}: {tool['description']}")
            
            # Test d'appel d'outil
            try:
                result = await client.call_tool("list_clients", {})
                print(f"Résultat: {result}")
            except Exception as e:
                print(f"Erreur: {e}")
    
    asyncio.run(test_mcp_client()) 