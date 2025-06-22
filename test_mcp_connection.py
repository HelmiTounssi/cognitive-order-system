#!/usr/bin/env python3
"""
Test simple de connexion MCP
"""

import asyncio
import json
import websockets

async def test_mcp_connection():
    """Test de connexion au serveur MCP"""
    try:
        print("🔗 Test de connexion au serveur MCP...")
        print("📍 URL: ws://localhost:8002")
        
        # Connexion WebSocket
        async with websockets.connect('ws://localhost:8002') as websocket:
            print("✅ Connexion WebSocket établie")
            
            # Test d'initialisation
            init_request = {
                "jsonrpc": "2.0",
                "id": "test_init",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "TestClient", "version": "1.0.0"}
                }
            }
            
            await websocket.send(json.dumps(init_request))
            print("📤 Requête d'initialisation envoyée")
            
            response = await websocket.recv()
            print(f"📥 Réponse reçue: {response}")
            
            # Test de liste des outils
            list_request = {
                "jsonrpc": "2.0",
                "id": "test_list",
                "method": "tools/list",
                "params": {}
            }
            
            await websocket.send(json.dumps(list_request))
            print("📤 Requête de liste des outils envoyée")
            
            response = await websocket.recv()
            print(f"📥 Réponse reçue: {response}")
            
            print("✅ Test de connexion MCP réussi!")
            
    except Exception as e:
        print(f"❌ Erreur de connexion MCP: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection()) 