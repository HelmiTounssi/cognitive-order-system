#!/usr/bin/env python3
"""
Test de la liste des clients
"""

import sys
import os

# Ajoute le répertoire parent au path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.knowledge_base import KnowledgeBase
from src.mcp.tools import add_client_tool, list_clients_tool

def test_client_operations():
    """Test des opérations sur les clients"""
    print("🧪 Test des opérations sur les clients")
    print("=" * 50)
    
    # Initialise la base de connaissances
    kb = KnowledgeBase()
    
    # Test 1: Ajouter un client
    print("\n1️⃣ Ajout d'un client...")
    success, message = add_client_tool("Test Client", "test@example.com", kb)
    print(f"Résultat: {message}")
    
    # Test 2: Lister les clients
    print("\n2️⃣ Liste des clients...")
    clients = list_clients_tool(kb)
    print(f"Nombre de clients trouvés: {len(clients)}")
    
    # Test 3: Ajouter un autre client
    print("\n3️⃣ Ajout d'un second client...")
    success, message = add_client_tool("Second Client", "second@example.com", kb)
    print(f"Résultat: {message}")
    
    # Test 4: Lister à nouveau
    print("\n4️⃣ Liste des clients (après ajout)...")
    clients = list_clients_tool(kb)
    print(f"Nombre de clients trouvés: {len(clients)}")
    
    # Test 5: Utiliser directement get_clients
    print("\n5️⃣ Test direct de get_clients...")
    direct_clients = kb.get_clients()
    print(f"get_clients() retourne: {len(direct_clients)} clients")
    for client in direct_clients:
        print(f"   - {client}")

if __name__ == "__main__":
    test_client_operations() 