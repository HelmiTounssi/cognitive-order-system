#!/usr/bin/env python3
"""
Point d'entrée principal du PoC - Système de Gestion Cognitif de Commande
Interface CLI interactive pour tester le système avec vrai LLM
"""

import os
import sys
from src.core.knowledge_base import KnowledgeBase
from src.rag.vector_store import VectorStore
from src.core.agent import CognitiveOrderAgent
from src.llm.llm_interface import LLMInterface


def print_banner():
    """Affiche la bannière du PoC"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🧠 Système de Gestion Cognitif de Commande               ║
║    Inférence Sémantique & Recherche Vectorielle             ║
║                                                              ║
║    PoC - Mind-Driven Design avec Vrai LLM                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Affiche l'aide et les exemples d'utilisation"""
    help_text = """
📖 GUIDE D'UTILISATION

🎯 EXEMPLES DE REQUÊTES :

1. Création de commande :
   • "Créer une nouvelle commande pour John Doe avec 3 unités de Super Laptop et traiter le paiement"
   • "Commander 2 Gaming Mouse pour Jane Smith"
   • "Passer une commande pour Bob Johnson : 1 Mechanical Keyboard avec 2 unités"

2. Validation de commande :
   • "Valider la commande O-12345678"
   • "Traiter la commande O-87654321"

3. Recommandations de produits :
   • "Je cherche un accessoire pour mon ordinateur portable"
   • "Quel produit recommanderiez-vous similaire à Gaming Mouse ?"
   • "Suggérer des produits gaming"

4. Vérification de statut :
   • "Statut de la commande O-12345678"
   • "Historique des commandes du client John Doe"

5. Autres commandes :
   • "help" - Afficher cette aide
   • "stats" - Afficher les statistiques du système
   • "llm_status" - Vérifier le statut du LLM
   • "quit" ou "exit" - Quitter le programme

🔧 FONCTIONNALITÉS DÉMONTRÉES :

• Inférence sémantique sur l'ontologie RDF
• Recherche vectorielle pour la similarité de produits
• Parsing en langage naturel avec vrai LLM
• Gestion des erreurs et alternatives intelligentes
• Orchestration d'outils métier
• Embeddings réels via API OpenAI

💡 CONSEILS :
• Utilisez des phrases naturelles
• Spécifiez clairement les noms de clients et produits
• Les IDs de commande sont générés automatiquement
• Le système gère les erreurs de stock et propose des alternatives
• Le LLM améliore la compréhension et les recommandations
    """
    print(help_text)


def print_stats(knowledge_base: KnowledgeBase, vector_store: VectorStore):
    """Affiche les statistiques du système"""
    print("\n📊 STATISTIQUES DU SYSTÈME")
    print("=" * 50)
    
    # Statistiques de la base de connaissances
    try:
        clients = knowledge_base.get_instances_of_class("http://example.org/ontology/Client")
        products = knowledge_base.get_instances_of_class("http://example.org/ontology/Product")
        orders = knowledge_base.get_instances_of_class("http://example.org/ontology/Order")
        
        print(f"👥 Clients: {len(clients)}")
        print(f"📦 Produits: {len(products)}")
        print(f"📋 Commandes: {len(orders)}")
        
        # Affiche quelques exemples
        if clients:
            print(f"\n👤 Exemples de clients:")
            for i, client_uri in enumerate(clients[:3], 1):
                client_id = client_uri.split('/')[-1]
                client_details = knowledge_base.get_client_details(client_id)
                print(f"   {i}. {client_details.get('hasName', 'N/A')} ({client_id})")
        
        if products:
            print(f"\n📦 Exemples de produits:")
            for i, product_uri in enumerate(products[:3], 1):
                product_id = product_uri.split('/')[-1]
                product_details = knowledge_base.get_product_details(product_id)
                print(f"   {i}. {product_details.get('hasName', 'N/A')} - {product_details.get('hasPrice', 'N/A')}€ ({product_id})")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des stats KB: {e}")
    
    # Statistiques de la base vectorielle
    try:
        vector_stats = vector_store.get_collection_stats()
        print(f"\n🔍 Base vectorielle:")
        print(f"   Collection: {vector_stats.get('collection_name', 'N/A')}")
        print(f"   Produits indexés: {vector_stats.get('total_products', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des stats vectorielles: {e}")
    
    print("=" * 50)


def check_llm_status(llm_interface: LLMInterface) -> bool:
    """Vérifie le statut de l'interface LLM"""
    try:
        print("\n🤖 STATUT DU LLM")
        print("=" * 30)
        
        if llm_interface:
            print("✅ Interface LLM initialisée")
            print(f"   Modèle: {llm_interface.model}")
            print(f"   Embedding: {llm_interface.embedding_model}")
            
            # Test simple de l'API
            test_embedding = llm_interface.generate_embedding("test")
            if test_embedding:
                print("✅ API OpenAI accessible")
                print(f"   Dimension embedding: {len(test_embedding)}")
                return True
            else:
                print("❌ Erreur lors du test de l'API")
                return False
        else:
            print("❌ Interface LLM non disponible")
            print("   Mode fallback activé (logique simulée)")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du LLM: {e}")
        return False


def initialize_system():
    """Initialise le système complet"""
    print("🚀 Initialisation du système...")
    
    try:
        # Initialisation de la base de connaissances
        print("📚 Chargement de la base de connaissances...")
        knowledge_base = KnowledgeBase()
        print("✅ Base de connaissances initialisée")
        
        # Initialisation de l'interface LLM
        llm_interface = None
        try:
            print("🤖 Initialisation de l'interface LLM...")
            llm_interface = LLMInterface()
            print("✅ Interface LLM initialisée")
        except Exception as e:
            print(f"⚠️ Interface LLM non disponible: {e}")
            print("   Le système fonctionnera en mode fallback")
        
        # Initialisation de la base vectorielle
        print("🔍 Initialisation de la base vectorielle...")
        vector_store = VectorStore(llm_interface=llm_interface)
        print("✅ Base vectorielle initialisée")
        
        # Initialisation de l'agent
        print("🤖 Initialisation de l'agent cognitif...")
        agent = CognitiveOrderAgent(knowledge_base, vector_store, llm_interface)
        print("✅ Agent cognitif initialisé")
        
        print("🎉 Système prêt à l'utilisation!")
        return knowledge_base, vector_store, agent, llm_interface
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        sys.exit(1)


def main():
    """Fonction principale"""
    print_banner()
    
    # Initialisation du système
    knowledge_base, vector_store, agent, llm_interface = initialize_system()
    
    print("\n" + "=" * 60)
    print("💬 Entrez vos requêtes en langage naturel (ou 'help' pour l'aide)")
    print("=" * 60)
    
    # Boucle interactive
    while True:
        try:
            # Lecture de la requête utilisateur
            user_input = input("\n🤔 Vous: ").strip()
            
            # Commandes spéciales
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Au revoir!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'stats':
                print_stats(knowledge_base, vector_store)
                continue
            elif user_input.lower() == 'llm_status':
                check_llm_status(llm_interface)
                continue
            elif not user_input:
                continue
            
            # Traitement de la requête par l'agent
            response = agent.run_agent(user_input)
            
            # Affichage de la réponse
            print(f"\n🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interruption détectée. Au revoir!")
            break
        except EOFError:
            print("\n\n👋 Fin de l'entrée. Au revoir!")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            print("💡 Essayez de reformuler votre requête ou tapez 'help' pour l'aide")


if __name__ == "__main__":
    main() 