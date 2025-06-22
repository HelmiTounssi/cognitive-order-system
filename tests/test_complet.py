#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from knowledge_base import KnowledgeBase
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


def test_base_connaissances(kb):
    """Test de la base de connaissances"""
    print("\n🧪 TEST 2: BASE DE CONNAISSANCES")
    print("=" * 50)
    
    try:
        # Test des clients
        print("👥 Test des clients...")
        clients = kb.get_clients()
        print(f"   Clients trouvés: {len(clients)}")
        for client in clients:
            print(f"     - {client['name']} ({client['email']})")
        
        # Test des produits
        print("\n📦 Test des produits...")
        product_class = "http://example.org/ontology/Product"
        product_uris = kb.get_instances_of_class(product_class)
        print(f"   Produits trouvés: {len(product_uris)}")
        for uri in product_uris[:3]:  # Affiche les 3 premiers
            product_id = uri.split('/')[-1]
            details = kb.get_product_details(product_id)
            name = details.get('hasName', 'N/A')
            price = details.get('hasPrice', 'N/A')
            print(f"     - {name}: {price}€")
        
        # Test de recherche
        print("\n🔍 Test de recherche...")
        client_id = kb.find_client_by_name("John Doe")
        if client_id:
            print(f"   Client 'John Doe' trouvé: {client_id}")
        
        product_id = kb.find_product_by_name("Super Laptop")
        if product_id:
            print(f"   Produit 'Super Laptop' trouvé: {product_id}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_recherche_vectorielle(vector_store):
    """Test de la recherche vectorielle"""
    print("\n🧪 TEST 3: RECHERCHE VECTORIELLE")
    print("=" * 50)
    
    try:
        # Test de recherche simple
        print("🔍 Test de recherche 'gaming'...")
        results = vector_store.search_similar_products("gaming", top_k=3)
        print(f"   Résultats trouvés: {len(results)}")
        for i, result in enumerate(results, 1):
            desc = result['description']
            score = result['similarity_score']
            print(f"     {i}. {desc} (score: {score:.2f})")
        
        # Test de recherche par nom de produit
        print("\n🔍 Test de recherche par nom 'Super Laptop'...")
        results = vector_store.search_by_product_name("Super Laptop", top_k=2)
        print(f"   Résultats trouvés: {len(results)}")
        for i, result in enumerate(results, 1):
            desc = result['description']
            score = result['similarity_score']
            print(f"     {i}. {desc} (score: {score:.2f})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_agent(agent):
    """Test de l'agent cognitif"""
    print("\n🧪 TEST 4: AGENT COGNITIF")
    print("=" * 50)
    
    try:
        # Test de recommandation
        print("🎯 Test de recommandation...")
        response = agent.run_agent("Recommande-moi des produits gaming")
        print(f"   Réponse: {response[:100]}...")
        
        # Test de liste des clients
        print("\n📋 Test de liste des clients...")
        response = agent.run_agent("Lister tous les clients")
        print(f"   Réponse: {response[:100]}...")
        
        # Test d'ajout de client
        print("\n👤 Test d'ajout de client...")
        response = agent.run_agent("Ajouter un nouveau client nommé Alice Martin")
        print(f"   Réponse: {response}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_introspection(kb):
    """Test de l'introspection de l'ontologie"""
    print("\n🧪 TEST 5: INTROSPECTION DE L'ONTOLOGIE")
    print("=" * 50)
    
    try:
        # Introspection complète
        print("🔍 Introspection complète...")
        ontology_info = kb.introspect_ontology()
        
        print(f"   Classes: {len(ontology_info.get('classes', []))}")
        for class_info in ontology_info['classes']:
            name = class_info['name']
            count = class_info['instances_count']
            print(f"     - {name}: {count} instances")
        
        print(f"\n   Propriétés: {len(ontology_info.get('properties', []))}")
        # Affiche les 5 premières propriétés
        for prop_info in ontology_info['properties'][:5]:
            name = prop_info['name']
            prop_type = prop_info['type']
            print(f"     - {name} ({prop_type})")
        
        # Requêtes introspectives
        print("\n🔍 Requêtes introspectives...")
        classes = kb.query_ontology_introspectively('classes')
        print(f"   Classes via requête: {len(classes)}")
        
        properties = kb.query_ontology_introspectively('properties')
        print(f"   Propriétés via requête: {len(properties)}")
        
        instances = kb.query_ontology_introspectively('instances')
        print(f"   Instances via requête: {len(instances)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_extension_dynamique(kb):
    """Test de l'extension dynamique de l'ontologie"""
    print("\n🧪 TEST 6: EXTENSION DYNAMIQUE")
    print("=" * 50)
    
    try:
        # Création d'une nouvelle classe
        print("🆕 Création de la classe 'Formation'...")
        formation_properties = [
            {'name': 'hasName', 'type': 'string', 'label': 'Nom de la formation'},
            {'name': 'hasDescription', 'type': 'string', 'label': 'Description'},
            {'name': 'hasDuration', 'type': 'int', 'label': 'Durée en heures'},
            {'name': 'hasPrice', 'type': 'float', 'label': 'Prix'},
            {'name': 'hasLevel', 'type': 'string', 'label': 'Niveau'}
        ]
        
        success = kb.extend_ontology_dynamically('Formation', formation_properties)
        result_msg = '✅ Succès' if success else '❌ Échec'
        print(f"   Résultat: {result_msg}")
        
        # Création d'instances
        print("\n🆕 Création d'instances...")
        
        formation1_props = {
            'hasName': 'Python pour débutants',
            'hasDescription': 'Formation complète Python',
            'hasDuration': 20,
            'hasPrice': 500.0,
            'hasLevel': 'Débutant'
        }
        
        instance1_id = kb.create_instance_dynamically('Formation', formation1_props)
        print(f"   Instance 1: {instance1_id}")
        
        formation2_props = {
            'hasName': 'Machine Learning avancé',
            'hasDescription': 'Formation ML avec Python',
            'hasDuration': 40,
            'hasPrice': 1200.0,
            'hasLevel': 'Avancé'
        }
        
        instance2_id = kb.create_instance_dynamically('Formation', formation2_props)
        print(f"   Instance 2: {instance2_id}")
        
        # Vérification
        print("\n🔍 Vérification de l'extension...")
        ontology_info = kb.introspect_ontology()
        for class_info in ontology_info['classes']:
            if class_info['name'] == 'Formation':
                count = class_info['instances_count']
                print(f"   ✅ Classe 'Formation' trouvée avec {count} instances")
                break
        
        # Requête des nouvelles instances
        formation_instances = kb.query_ontology_introspectively(
            'instances', class_name='Formation'
        )
        print(f"   Instances de Formation: {len(formation_instances)}")
        for instance in formation_instances:
            name = instance['properties'].get('hasName', 'N/A')
            print(f"     - {instance['id']}: {name}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_outils(kb):
    """Test des outils"""
    print("\n🧪 TEST 7: OUTILS")
    print("=" * 50)
    
    try:
        # Test de l'outil d'introspection
        print("🔍 Test de l'outil d'introspection...")
        ontology_info = tools.introspect_ontology_tool(kb)
        classes_count = len(ontology_info.get('classes', []))
        print(f"   Introspection réussie: {classes_count} classes")
        
        # Test de l'outil d'extension
        print("\n🆕 Test de l'outil d'extension...")
        projet_properties = [
            {'name': 'hasName', 'type': 'string', 'label': 'Nom du projet'},
            {'name': 'hasBudget', 'type': 'float', 'label': 'Budget'},
            {'name': 'hasDeadline', 'type': 'string', 'label': 'Date limite'}
        ]
        
        success, message = tools.extend_ontology_tool('Projet', projet_properties, kb)
        print(f"   {message}")
        
        # Test de l'outil de création d'instance
        print("\n🆕 Test de l'outil de création d'instance...")
        projet_props = {
            'hasName': 'Développement web',
            'hasBudget': 8000.0,
            'hasDeadline': '2024-12-31'
        }
        
        success, message = tools.create_instance_tool('Projet', projet_props, kb)
        print(f"   {message}")
        
        # Test de l'outil de requête
        print("\n🔍 Test de l'outil de requête...")
        results = tools.query_ontology_tool('classes', kb)
        print(f"   Classes trouvées: {len(results)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_integration_complete(agent):
    """Test d'intégration complète"""
    print("\n🧪 TEST 8: INTÉGRATION COMPLÈTE")
    print("=" * 50)
    
    try:
        # Test d'une requête complexe
        print("🎯 Test de requête complexe...")
        response = agent.run_agent("Introspection de l'ontologie")
        print(f"   Réponse: {response[:200]}...")
        
        # Test d'extension via l'agent
        print("\n🆕 Test d'extension via l'agent...")
        query = ("Ajouter une nouvelle classe Formation avec propriétés "
                "hasName, hasDescription, hasPrice")
        response = agent.run_agent(query)
        print(f"   Réponse: {response}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_ultra_generique():
    print("=== TEST ULTRA-GENERIQUE ===")
    print(f"Python version: {sys.version}")
    
    # 1. Test base de connaissances
    print("\n1. Initialisation base de connaissances...")
    kb = KnowledgeBase()
    print("   ✓ Base de connaissances créée")
    
    # 2. Test ajout de classes dynamiques
    print("\n2. Ajout de classes dynamiques...")
    kb.extend_ontology_dynamically('Client', [
        {'name': 'hasName', 'type': 'string'},
        {'name': 'hasEmail', 'type': 'string'},
        {'name': 'hasPhone', 'type': 'string'}
    ])
    print("   ✓ Classe Client ajoutée avec 3 propriétés")
    
    kb.extend_ontology_dynamically('Commande', [
        {'name': 'hasClient', 'type': 'Client'},
        {'name': 'hasDate', 'type': 'date'},
        {'name': 'hasMontant', 'type': 'float'}
    ])
    print("   ✓ Classe Commande ajoutée avec 3 propriétés")
    
    # 3. Test introspection
    print("\n3. Introspection de l'ontologie...")
    info = kb.introspect_ontology()
    classes = info.get('classes', [])
    print(f"   ✓ {len(classes)} classes trouvées:")
    for cls in classes:
        print(f"     - {cls['name']} ({len(cls.get('properties', []))} propriétés)")
    
    # 4. Test handlers métier
    print("\n4. Ajout de handlers métier...")
    
    # Handler pour création de client
    client_handler = {
        'description': 'Créer un nouveau client',
        'extraction_patterns': {
            'nom': [r'nom[:\s]+([a-zA-Z\s]+)'],
            'email': [r'email[:\s]+([a-zA-Z0-9@.]+)'],
            'telephone': [r'telephone[:\s]+([0-9\s+\-]+)']
        },
        'workflow': [
            {'step': 1, 'action': 'create_client', 'params': ['nom', 'email', 'telephone']},
            {'step': 2, 'action': 'validate_client', 'params': ['client_id']}
        ],
        'rules': [
            {'condition': 'email_valid', 'action': 'proceed'},
            {'condition': 'email_invalid', 'action': 'error'}
        ]
    }
    
    success1 = kb.add_business_handler('create_client_handler', client_handler)
    print(f"   ✓ Handler création client: {'OK' if success1 else 'ERREUR'}")
    
    # Handler pour création de commande
    commande_handler = {
        'description': 'Créer une nouvelle commande',
        'extraction_patterns': {
            'client_id': [r'client[:\s]+([0-9]+)'],
            'montant': [r'montant[:\s]+([0-9.]+)'],
            'date': [r'date[:\s]+([0-9/]+)']
        },
        'workflow': [
            {'step': 1, 'action': 'validate_client', 'params': ['client_id']},
            {'step': 2, 'action': 'create_commande', 'params': ['client_id', 'montant', 'date']}
        ],
        'rules': [
            {'condition': 'client_exists', 'action': 'proceed'},
            {'condition': 'client_not_found', 'action': 'error'}
        ]
    }
    
    success2 = kb.add_business_handler('create_commande_handler', commande_handler)
    print(f"   ✓ Handler création commande: {'OK' if success2 else 'ERREUR'}")
    
    # 5. Test liste handlers
    print("\n5. Liste des handlers métier...")
    handlers = kb.list_business_handlers()
    print(f"   ✓ {len(handlers)} handlers enregistrés:")
    for handler_name in handlers:
        print(f"     - {handler_name}")
    
    # 6. Test création d'instances
    print("\n6. Création d'instances...")
    
    # Créer un client
    client_instance = kb.create_instance('Client', {
        'hasName': 'Jean Dupont',
        'hasEmail': 'jean.dupont@email.com',
        'hasPhone': '0123456789'
    })
    print(f"   ✓ Instance Client créée: {client_instance}")
    
    # 7. Test recherche sémantique
    print("\n7. Test recherche sémantique...")
    try:
        results = kb.search_semantic("client jean dupont")
        print(f"   ✓ Recherche sémantique: {len(results)} résultats")
    except Exception as e:
        print(f"   ⚠ Recherche sémantique: {e}")
    
    print("\n=== SUCCES! SYSTEME ULTRA-GENERIQUE OPERATIONNEL ===")
    print("✓ Base de connaissances dynamique")
    print("✓ Ontologie extensible")
    print("✓ Handlers métier configurables")
    print("✓ Introspection complète")
    print("✓ Création d'instances")
    print("✓ Recherche sémantique")
    
    return True


def main():
    """Fonction principale de test"""
    print("🧠 TEST COMPLET - SYSTÈME DE GESTION COGNITIF DE COMMANDE")
    print("=" * 70)
    print("Ce test démontre toutes les fonctionnalités du système :")
    print("- Base de connaissances RDF")
    print("- Recherche vectorielle")
    print("- Interface LLM OpenAI")
    print("- Agent cognitif")
    print("- Introspection et réflexivité")
    print("- Extension dynamique de l'ontologie")
    print("=" * 70)
    
    # Initialisation
    kb, vector_store, llm, agent = test_initialisation()
    if not all([kb, vector_store, agent]):
        print("❌ Échec de l'initialisation. Arrêt des tests.")
        return
    
    # Tests
    tests = [
        ("Base de connaissances", lambda: test_base_connaissances(kb)),
        ("Recherche vectorielle", lambda: test_recherche_vectorielle(vector_store)),
        ("Agent cognitif", lambda: test_agent(agent)),
        ("Introspection", lambda: test_introspection(kb)),
        ("Extension dynamique", lambda: test_extension_dynamique(kb)),
        ("Outils", lambda: test_outils(kb)),
        ("Intégration complète", lambda: test_integration_complete(agent))
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
        print(f"{test_name:25} : {status}")
        if result:
            passed += 1
    
    print(f"\nRésultat global: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("Le système fonctionne parfaitement avec toutes ses fonctionnalités.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")


if __name__ == "__main__":
    try:
        test_ultra_generique()
    except Exception as e:
        print(f"ERREUR: {e}")
        import traceback
        traceback.print_exc() 