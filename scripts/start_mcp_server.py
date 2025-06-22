#!/usr/bin/env python3
"""
Script de démarrage du serveur MCP complet
"""

import asyncio
import sys
import os

# Ajoute le répertoire parent (racine du projet) au path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Remonte d'un niveau
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    from src.mcp.mcp_server import start_mcp_server
    from src.core.knowledge_base import KnowledgeBase
    from src.rag.vector_store import VectorStore
    
    print("🚀 Démarrage du serveur MCP complet...")
    print("📍 Port: 8002")
    print("🌐 URL: ws://localhost:8002")
    print("=" * 50)
    
    async def main():
        try:
            # Initialise les composants
            kb = KnowledgeBase()
            vs = VectorStore()
            
            # Démarre le serveur MCP
            await start_mcp_server(kb, vs, host="localhost", port=8002)
            
        except KeyboardInterrupt:
            print("\n🛑 Serveur MCP arrêté par l'utilisateur")
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du serveur MCP: {e}")
    
    asyncio.run(main()) 