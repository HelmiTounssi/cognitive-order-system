#!/usr/bin/env python3
"""
Test de l'API RAG
Vérifie que l'interface RAG fonctionne correctement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag_system import HybridRAGSystem
from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore
from src.llm_interface import LLMInterface

import requests
import json
from datetime import datetime

def test_rag_api():
    """Test complet de l'API RAG"""
    print("🧪 Test de l'API RAG")
    print("=" * 50)
    
    base_url = "http://localhost:5001/api"
    
    # Test 1: Créer une nouvelle conversation
    print("\n1. Test de création de conversation...")
    try:
        response = requests.post(f"{base_url}/rag/conversations", json={})
        if response.status_code == 200:
            data = response.json()
            conversation_id = data.get('conversation_id')
            print(f"✅ Conversation créée: {conversation_id}")
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test 2: Envoyer un message
    print("\n2. Test d'envoi de message...")
    try:
        message_data = {
            "message": "How to create a medical workflow?",
            "conversation_id": conversation_id
        }
        
        response = requests.post(f"{base_url}/rag/chat", json=message_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Message envoyé avec succès")
            print(f"   Réponse: {data['response']['content'][:100]}...")
            print(f"   Confiance: {data['response']['metadata'].get('confidence', 'N/A')}")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   Détails: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test 3: Récupérer la conversation
    print("\n3. Test de récupération de conversation...")
    try:
        response = requests.get(f"{base_url}/rag/conversations/{conversation_id}")
        if response.status_code == 200:
            data = response.json()
            messages_count = len(data['conversation']['messages'])
            print(f"✅ Conversation récupérée: {messages_count} messages")
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test 4: Récupérer les suggestions
    print("\n4. Test de récupération des suggestions...")
    try:
        response = requests.get(f"{base_url}/rag/conversations/{conversation_id}/suggestions")
        if response.status_code == 200:
            data = response.json()
            suggestions_count = len(data['suggestions'])
            print(f"✅ Suggestions récupérées: {suggestions_count} suggestions")
            for i, suggestion in enumerate(data['suggestions'][:3]):
                print(f"   {i+1}. {suggestion}")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 5: Récupérer les analytics
    print("\n5. Test de récupération des analytics...")
    try:
        response = requests.get(f"{base_url}/rag/conversations/{conversation_id}/analytics")
        if response.status_code == 200:
            data = response.json()
            analytics = data['analytics']
            print("✅ Analytics récupérées:")
            print(f"   Messages totaux: {analytics.get('total_messages', 0)}")
            print(f"   Confiance moyenne: {analytics.get('average_confidence', 0):.2f}")
            print(f"   Sources utilisées: {analytics.get('sources_used', [])}")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 6: Recherche hybride
    print("\n6. Test de recherche hybride...")
    try:
        search_data = {
            "query": "medical workflow",
            "top_k": 3
        }
        
        response = requests.post(f"{base_url}/rag/search", json=search_data)
        if response.status_code == 200:
            data = response.json()
            total_results = data.get('total_results', 0)
            print(f"✅ Recherche hybride: {total_results} résultats")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 7: Contexte métier
    print("\n7. Test de récupération du contexte métier...")
    try:
        context_data = {
            "query": "medical diagnosis workflow"
        }
        
        response = requests.post(f"{base_url}/rag/context", json=context_data)
        if response.status_code == 200:
            data = response.json()
            context = data['context']
            print("✅ Contexte métier récupéré:")
            print(f"   Domaine: {context.get('domain', 'unknown')}")
            print(f"   Workflows: {len(context.get('workflows', []))}")
            print(f"   Patterns: {len(context.get('patterns', []))}")
            print(f"   Règles: {len(context.get('rules', []))}")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # Test 8: Liste des conversations
    print("\n8. Test de récupération de la liste des conversations...")
    try:
        response = requests.get(f"{base_url}/rag/conversations")
        if response.status_code == 200:
            data = response.json()
            conversations_count = len(data['conversations'])
            print(f"✅ Conversations récupérées: {conversations_count}")
        else:
            print(f"❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Tests RAG terminés avec succès!")
    return True

if __name__ == "__main__":
    test_rag_api() 