#!/usr/bin/env python3
"""
Test du Proxy Sémantique et de la Réflexion
Démonstration des équivalents sémantiques des Dynamic Proxy et de la réflexion en POO
"""

from knowledge_base import KnowledgeBase, SemanticProxy
from vector_store import VectorStore
from llm_interface import LLMInterface
from agent import CognitiveOrderAgent
import tools


def test_initialisation():
    """Test de l'initialisation du système"""
    print("🧪 TEST 1: INITIALISATION DU SYSTÈME")
    print("=" * 50)
    
    try:
        # Test de la base de connaissances
        print("📚 Test de la base de connaissances...")
        kb = KnowledgeBase()
        print("   ✅ Base de connaissances initialisée")
        
        # Test de l'interface LLM
        print("🤖 Test de l'interface LLM...")
        try:
            llm = LLMInterface()
            print("   ✅ Interface LLM initialisée (OpenAI)")
        except Exception as e:
            print(f"   ⚠️ Interface LLM non disponible: {e}")
            llm = None
        
        # Test de la base vectorielle
        print("🔍 Test de la base vectorielle...")
        vector_store = VectorStore(llm_interface=llm)
        print("   ✅ Base vectorielle initialisée")
        
        # Test de l'agent
        print("🧠 Test de l'agent cognitif...")
        agent = CognitiveOrderAgent(kb, vector_store, llm)
        print("   ✅ Agent cognitif initialisé")
        
        return kb, vector_store, llm, agent
        
    except Exception as e:
        print(f"   ❌ Erreur lors de l'initialisation: {e}")
        return None, None, None, None


def test_creation_classes_comportementales(kb):
    """Test de création de classes avec comportements"""
    print("\n🧪 TEST 2: CRÉATION DE CLASSES COMPORTEMENTALES")
    print("=" * 50)
    
    try:
        # Création de la classe Client avec comportements
        print("🆕 Création de la classe Client avec comportements...")
        client_methods = [
            {
                'name': 'passer_commande',
                'parameters': [
                    {'name': 'produits', 'type': 'List[Product]'},
                    {'name': 'quantite', 'type': 'int'}
                ],
                'return_type': 'Order'
            },
            {
                'name': 'payer',
                'parameters': [
                    {'name': 'montant', 'type': 'float'},
                    {'name': 'methode', 'type': 'string'}
                ],
                'return_type': 'Payment'
            },
            {
                'name': 'modifier_profil',
                'parameters': [
                    {'name': 'nouveau_nom', 'type': 'string'},
                    {'name': 'nouveau_email', 'type': 'string'}
                ],
                'return_type': 'Client'
            }
        ]
        
        success = kb.add_behavior_class('Client', client_methods)
        print(f"   Résultat: {'✅ Succès' if success else '❌ Échec'}")
        
        # Création de la classe Order avec machine à états
        print("\n🆕 Création de la classe Order avec machine à états...")
        order_states = ['en_attente', 'validee', 'payee', 'livree', 'annulee']
        order_transitions = [
            {'from': 'en_attente', 'to': 'validee', 'trigger': 'validation'},
            {'from': 'validee', 'to': 'payee', 'trigger': 'paiement'},
            {'from': 'payee', 'to': 'livree', 'trigger': 'livraison'},
            {'from': 'en_attente', 'to': 'annulee', 'trigger': 'annulation'},
            {'from': 'validee', 'to': 'annulee', 'trigger': 'annulation'}
        ]
        
        success = kb.add_state_machine('Order', order_states, order_transitions)
        print(f"   Résultat: {'✅ Succès' if success else '❌ Échec'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_proxy_semantique(kb):
    """Test du proxy sémantique"""
    print("\n🧪 TEST 3: PROXY SÉMANTIQUE")
    print("=" * 50)
    
    try:
        # Création du gestionnaire de proxy
        print("🔧 Création du gestionnaire de proxy...")
        proxy_manager = SemanticProxy(kb)
        print("   ✅ Gestionnaire de proxy créé")
        
        # Création d'un proxy pour la classe Client
        print("\n🔧 Création d'un proxy pour la classe Client...")
        client_proxy = proxy_manager.create_proxy('Client')
        if client_proxy:
            print("   ✅ Proxy pour la classe Client créé")
        else:
            print("   ❌ Échec de création du proxy")
            return False
        
        # Création d'instances de test
        print("\n🆕 Création d'instances de test...")
        john_props = {'hasName': 'John Doe', 'hasEmail': 'john@email.com'}
        john_id = kb.create_instance_dynamically('Client', john_props)
        print(f"   Instance John créée: {john_id}")
        
        alice_props = {'hasName': 'Alice Martin', 'hasEmail': 'alice@email.com'}
        alice_id = kb.create_instance_dynamically('Client', alice_props)
        print(f"   Instance Alice créée: {alice_id}")
        
        # Création de proxies pour les instances
        print("\n🔧 Création de proxies pour les instances...")
        john_proxy = proxy_manager.create_proxy('Client', john_id)
        alice_proxy = proxy_manager.create_proxy('Client', alice_id)
        
        if john_proxy and alice_proxy:
            print("   ✅ Proxies pour les instances créés")
        else:
            print("   ❌ Échec de création des proxies d'instances")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_reflection(kb):
    """Test de la réflexion"""
    print("\n🧪 TEST 4: RÉFLEXION")
    print("=" * 50)
    
    try:
        proxy_manager = SemanticProxy(kb)
        
        # Réflexion sur la classe Client
        print("🔍 Réflexion sur la classe Client...")
        structure = proxy_manager.reflect_class_structure('Client')
        
        if structure:
            print(f"   Classe: {structure.get('class_name', 'N/A')}")
            print(f"   URI: {structure.get('class_uri', 'N/A')}")
            print(f"   Propriétés: {len(structure.get('properties', []))}")
            print(f"   Méthodes: {len(structure.get('methods', []))}")
            print(f"   Instances: {structure.get('instances_count', 0)}")
            
            # Détail des méthodes
            print("\n   Méthodes disponibles:")
            for method in structure.get('methods', []):
                params = [p['name'] for p in method.get('parameters', [])]
                print(f"     - {method['name']}({', '.join(params)}) -> {method.get('return_type', 'void')}")
        else:
            print("   ❌ Réflexion échouée")
            return False
        
        # Liste des méthodes disponibles
        print("\n📋 Liste des méthodes via proxy...")
        methods = proxy_manager.list_available_methods('Client')
        print(f"   Méthodes trouvées: {len(methods)}")
        for method in methods:
            print(f"     - {method['name']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_execution_reflexive(kb):
    """Test de l'exécution réflexive de méthodes"""
    print("\n🧪 TEST 5: EXÉCUTION RÉFLEXIVE")
    print("=" * 50)
    
    try:
        proxy_manager = SemanticProxy(kb)
        
        # Récupère une instance existante
        instances = kb.get_instances_of_class("http://example.org/ontology/Client")
        if not instances:
            print("   ❌ Aucune instance Client trouvée")
            return False
        
        instance_id = instances[0].split('/')[-1]
        print(f"   Utilisation de l'instance: {instance_id}")
        
        # Création du proxy pour cette instance
        proxy = proxy_manager.create_proxy('Client', instance_id)
        if not proxy:
            print("   ❌ Échec de création du proxy")
            return False
        
        # Test d'exécution de méthodes par réflexion
        print("\n🔄 Test d'exécution de méthodes...")
        
        # Test passer_commande
        print("   Test passer_commande...")
        try:
            result = proxy._execute_method('passer_commande', produits=['laptop_123'], quantite=2)
            print(f"     Résultat: {result}")
        except Exception as e:
            print(f"     Erreur: {e}")
        
        # Test payer
        print("   Test payer...")
        try:
            result = proxy._execute_method('payer', montant=1200.0, methode='carte')
            print(f"     Résultat: {result}")
        except Exception as e:
            print(f"     Erreur: {e}")
        
        # Test modifier_profil
        print("   Test modifier_profil...")
        try:
            result = proxy._execute_method('modifier_profil', nouveau_nom='John Smith', nouveau_email='john.smith@email.com')
            print(f"     Résultat: {result}")
        except Exception as e:
            print(f"     Erreur: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_outils_proxy(kb):
    """Test des outils de proxy"""
    print("\n🧪 TEST 6: OUTILS DE PROXY")
    print("=" * 50)
    
    try:
        # Test de création de proxy via outil
        print("🔧 Test de création de proxy via outil...")
        success, message = tools.create_semantic_proxy_tool(kb, 'Client', None)
        print(f"   {message}")
        
        # Test de réflexion via outil
        print("\n🔍 Test de réflexion via outil...")
        success, message = tools.reflect_class_tool('Client', kb)
        if success:
            print("   ✅ Réflexion réussie")
            print(message[:200] + "..." if len(message) > 200 else message)
        else:
            print(f"   ❌ {message}")
        
        # Test de liste des méthodes via outil
        print("\n📋 Test de liste des méthodes via outil...")
        success, message = tools.list_proxy_methods_tool('Client', kb)
        if success:
            print("   ✅ Liste des méthodes réussie")
            print(message[:200] + "..." if len(message) > 200 else message)
        else:
            print(f"   ❌ {message}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_agent_proxy(agent):
    """Test de l'agent avec les nouvelles fonctionnalités de proxy"""
    print("\n🧪 TEST 7: AGENT AVEC PROXY")
    print("=" * 50)
    
    try:
        # Test de réflexion via l'agent
        print("🔍 Test de réflexion via l'agent...")
        response = agent.run_agent("Réflexion sur la classe Client")
        print(f"   Réponse: {response[:100]}...")
        
        # Test de création de proxy via l'agent
        print("\n🔧 Test de création de proxy via l'agent...")
        response = agent.run_agent("Créer un proxy sémantique pour la classe Client")
        print(f"   Réponse: {response}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def main():
    """Fonction principale de test"""
    print("🔧 TEST PROXY SÉMANTIQUE ET RÉFLEXION")
    print("=" * 70)
    print("Ce test démontre les équivalents sémantiques de :")
    print("- Dynamic Proxy en POO")
    print("- Réflexion et introspection")
    print("- Exécution dynamique de méthodes")
    print("- Instanciation par réflexion")
    print("=" * 70)
    
    # Initialisation
    kb, vector_store, llm, agent = test_initialisation()
    if not all([kb, vector_store, agent]):
        print("❌ Échec de l'initialisation. Arrêt des tests.")
        return
    
    # Tests
    tests = [
        ("Création de classes comportementales", lambda: test_creation_classes_comportementales(kb)),
        ("Proxy sémantique", lambda: test_proxy_semantique(kb)),
        ("Réflexion", lambda: test_reflection(kb)),
        ("Exécution réflexive", lambda: test_execution_reflexive(kb)),
        ("Outils de proxy", lambda: test_outils_proxy(kb)),
        ("Agent avec proxy", lambda: test_agent_proxy(agent))
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans le test '{test_name}': {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:30} : {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("Le système de proxy sémantique et de réflexion fonctionne parfaitement.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")


if __name__ == "__main__":
    main() 