#!/usr/bin/env python3
"""
Démonstration simple du serveur MCP
"""

import asyncio
import sys
import os

# Ajoute le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore
from src.agent import CognitiveOrderAgent


def demo_mcp():
    """
    Démonstration simple de l'utilisation de MCP
    """
    print("🚀 Démonstration du serveur MCP")
    print("=" * 40)
    
    # Initialisation
    print("1. Initialisation des composants...")
    kb = KnowledgeBase()
    vs = VectorStore()
    
    # Agent sans MCP (local)
    print("2. Test avec agent local...")
    agent_local = CognitiveOrderAgent(
        knowledge_base=kb,
        vector_store=vs,
        use_mcp=False
    )
    
    # Test local
    response_local = agent_local.run_agent("lister les clients")
    print(f"   Réponse locale: {response_local[:100]}...")
    
    # Agent avec MCP (si disponible)
    print("3. Test avec agent MCP...")
    agent_mcp = CognitiveOrderAgent(
        knowledge_base=kb,
        vector_store=vs,
        use_mcp=True,
        mcp_server_url="ws://localhost:8001"
    )
    
    # Test MCP
    response_mcp = agent_mcp.run_agent("lister les clients")
    print(f"   Réponse MCP: {response_mcp[:100]}...")
    
    # Comparaison
    print("4. Comparaison:")
    if "MCP non disponible" in response_mcp:
        print("   ❌ Serveur MCP non disponible - utilisez 'python start_mcp_server.py'")
        print("   ✅ Agent local fonctionne correctement")
    else:
        print("   ✅ Serveur MCP disponible et fonctionnel")
        print("   ✅ Agent MCP fonctionne correctement")
    
    print("\n📋 Instructions:")
    print("   - Pour démarrer le serveur MCP: python start_mcp_server.py")
    print("   - Pour tester l'intégration: python test_mcp_integration.py")
    print("   - Pour plus d'infos: voir README_MCP.md")


if __name__ == "__main__":
    demo_mcp() 