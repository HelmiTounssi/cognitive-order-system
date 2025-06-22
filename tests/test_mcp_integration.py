#!/usr/bin/env python3
"""
Script de test pour l'intégration MCP
Démontre l'utilisation du serveur MCP avec l'agent
"""

import asyncio
import sys
import os
import time
import threading

# Ajoute le répertoire src au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.knowledge_base import KnowledgeBase
from src.rag.vector_store import VectorStore
from src.core.agent import CognitiveOrderAgent
from src.mcp.mcp_server import start_mcp_server


def start_mcp_server_thread():
    """
    Démarre le serveur MCP dans un thread séparé
    """
    def run_server():
        kb = KnowledgeBase()
        vs = VectorStore()
        asyncio.run(start_mcp_server(kb, vs, host="localhost", port=8001))
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_thread


def test_mcp_integration():
    """
    Teste l'intégration MCP avec l'agent
    """
    print("🚀 Test d'intégration MCP")
    print("=" * 50)
    
    # Démarre le serveur MCP
    print("1. Démarrage du serveur MCP...")
    server_thread = start_mcp_server_thread()
    time.sleep(2)  # Attend que le serveur démarre
    
    # Initialise les composants
    print("2. Initialisation des composants...")
    kb = KnowledgeBase()
    vs = VectorStore()
    
    # Crée l'agent avec MCP activé
    print("3. Création de l'agent avec MCP...")
    agent = CognitiveOrderAgent(
        knowledge_base=kb,
        vector_store=vs,
        use_mcp=True,
        mcp_server_url="ws://localhost:8001"
    )
    
    # Test des fonctionnalités MCP
    print("4. Test des fonctionnalités MCP...")
    
    # Liste les outils disponibles
    print("\n📋 Outils disponibles via MCP:")
    tools_list = agent.list_available_tools_via_mcp()
    print(tools_list)
    
    # Test d'appel d'outil direct
    print("\n🔧 Test d'appel d'outil direct:")
    result = agent.call_tool_via_mcp("list_clients", {})
    print(result)
    
    # Test d'exécution d'intention via MCP
    print("\n🎯 Test d'exécution d'intention via MCP:")
    test_queries = [
        "lister les clients",
        "voir la structure de l'ontologie",
        "lister toutes les commandes"
    ]
    
    for query in test_queries:
        print(f"\nRequête: {query}")
        response = agent.run_agent(query)
        print(f"Réponse: {response}")
        time.sleep(1)
    
    print("\n✅ Test d'intégration MCP terminé!")


def test_mcp_vs_local():
    """
    Compare les performances MCP vs local
    """
    print("\n🔍 Comparaison MCP vs Local")
    print("=" * 50)
    
    kb = KnowledgeBase()
    vs = VectorStore()
    
    # Test avec MCP
    print("1. Test avec MCP activé...")
    agent_mcp = CognitiveOrderAgent(
        knowledge_base=kb,
        vector_store=vs,
        use_mcp=True
    )
    
    start_time = time.time()
    result_mcp = agent_mcp.run_agent("lister les clients")
    mcp_time = time.time() - start_time
    
    # Test sans MCP
    print("2. Test sans MCP (local)...")
    agent_local = CognitiveOrderAgent(
        knowledge_base=kb,
        vector_store=vs,
        use_mcp=False
    )
    
    start_time = time.time()
    result_local = agent_local.run_agent("lister les clients")
    local_time = time.time() - start_time
    
    # Comparaison
    print(f"\n📊 Comparaison des performances:")
    print(f"   MCP: {mcp_time:.3f}s")
    print(f"   Local: {local_time:.3f}s")
    print(f"   Différence: {abs(mcp_time - local_time):.3f}s")
    
    print(f"\n📋 Résultats:")
    print(f"   MCP: {result_mcp[:100]}...")
    print(f"   Local: {result_local[:100]}...")


if __name__ == "__main__":
    try:
        test_mcp_integration()
        test_mcp_vs_local()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc() 