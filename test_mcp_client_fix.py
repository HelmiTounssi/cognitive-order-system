#!/usr/bin/env python3
"""
Test de correction du problème de liste des clients via MCP
"""

import sys
import os
import asyncio
import websockets
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_mcp_client_tools():
    """Test des outils MCP pour les clients"""
    print("🧪 Test des outils MCP pour les clients...")
    
    uri = "ws://localhost:8002"
    
    try:
        async with websockets.connect(uri) as websocket:
            # Test 1: Ajouter un client
            print("📝 Test d'ajout de client...")
            add_client_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "add_client",
                    "arguments": {
                        "name": "Test MCP User",
                        "email": "test.mcp@example.com"
                    }
                }
            }
            
            await websocket.send(json.dumps(add_client_request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if "result" in result:
                print(f"   ✅ Client ajouté: {result['result']}")
            else:
                print(f"   ❌ Erreur: {result}")
                return False
            
            # Test 2: Lister les clients
            print("📋 Test de liste des clients...")
            list_clients_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "list_clients",
                    "arguments": {}
                }
            }
            
            await websocket.send(json.dumps(list_clients_request))
            response = await websocket.recv()
            result = json.loads(response)
            
            if "result" in result:
                clients = result['result']
                print(f"   📊 Nombre de clients trouvés: {len(clients)}")
                for client in clients:
                    print(f"   - {client['name']} ({client['email']}) - ID: {client['id']}")
                return len(clients) > 0
            else:
                print(f"   ❌ Erreur: {result}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_client_tools())
    if success:
        print("\n✅ Test MCP réussi ! Le problème de liste des clients est corrigé.")
    else:
        print("\n❌ Test MCP échoué ! Le problème persiste.") 