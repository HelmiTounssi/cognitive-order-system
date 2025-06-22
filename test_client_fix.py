#!/usr/bin/env python3
"""
Test de correction du problème de liste des clients
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.knowledge_base import KnowledgeBase
from src.rag.vector_store import VectorStore

def test_client_list():
    """Test de création et liste des clients"""
    print("🧪 Test de correction du problème de liste des clients...")
    
    # Initialise la base de connaissances
    vector_store = VectorStore()
    kb = KnowledgeBase(vector_store)
    
    # Ajoute un client
    print("📝 Ajout d'un client...")
    client_id = kb.add_client("test_client_123", "Test User", "test@example.com")
    print(f"   ✅ Client ajouté: {client_id}")
    
    # Liste les clients
    print("📋 Liste des clients...")
    clients = kb.get_clients()
    print(f"   📊 Nombre de clients trouvés: {len(clients)}")
    
    for client in clients:
        print(f"   - {client['name']} ({client['email']}) - ID: {client['id']}")
    
    return len(clients) > 0

if __name__ == "__main__":
    success = test_client_list()
    if success:
        print("\n✅ Test réussi ! Le problème de liste des clients est corrigé.")
    else:
        print("\n❌ Test échoué ! Le problème persiste.") 