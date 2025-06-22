#!/usr/bin/env python3
"""
Script de démarrage du serveur MCP simplifié
"""

import asyncio
import sys
import os

# Ajoute le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from src.mcp.mcp_server_simple import start_simple_mcp_server
    
    print("🚀 Démarrage du serveur MCP simplifié...")
    print("📍 Port: 8002")
    print("🌐 URL: ws://localhost:8002")
    print("=" * 50)
    
    try:
        asyncio.run(start_simple_mcp_server(port=8002))
    except KeyboardInterrupt:
        print("\n🛑 Serveur MCP arrêté par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du serveur MCP: {e}") 