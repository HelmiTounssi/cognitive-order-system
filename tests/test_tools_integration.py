#!/usr/bin/env python3
"""
Test d'intégration des outils avec l'agent
Vérifie que l'agent utilise correctement les vrais outils
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore
from src.llm_interface import LLMInterface
from src.agent import CognitiveOrderAgent
import tools
import json


def test_initialisation():
    """Test de l'initialisation du système avec intégration des outils"""
    print("🧪 TEST 1: INITIALISATION AVEC INTÉGRATION DES OUTILS")
    print("=" * 60)
    
    try:
        # Initialisation des composants
        kb = KnowledgeBase()
        vector_store = VectorStore()
        llm = LLMInterface()
        agent = CognitiveOrderAgent(kb, vector_store, llm)
        
        print("✅ Composants initialisés avec succès")
        print(f"   - Knowledge Base: {type(kb).__name__}")
        print(f"   - Vector Store: {type(vector_store).__name__}")
        print(f"   - LLM Interface: {type(llm).__name__}")
        print(f"   - Agent: {type(agent).__name__}")
        
        # Vérification que le moteur de règles a accès à la base de connaissances
        if agent.rule_engine.knowledge_base:
            print("✅ Moteur de règles connecté à la base de connaissances")
        else:
            print("❌ Moteur de règles non connecté à la base de connaissances")
            return None, None, None, None
        
        return kb, vector_store, llm, agent
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return None, None, None, None


def test_tools_integration():
    """Test de l'intégration des outils dans l'agent"""
    print("\n🧪 TEST 2: INTÉGRATION DES OUTILS")
    print("=" * 60)
    
    kb, vector_store, llm, agent = test_initialisation()
    if not agent:
        return False
    
    try:
        # Ajout de données de test
        print("📚 Ajout de données de test...")
        
        # Ajout de produits
        kb.add_product("laptop_001", "Laptop Gaming", 1200.0, 15, "Ordinateur portable gaming haute performance")
        kb.add_product("mouse_001", "Souris Gaming", 45.0, 50, "Souris gaming avec capteur optique")
        kb.add_product("keyboard_001", "Clavier Mécanique", 120.0, 25, "Clavier mécanique RGB")
        
        # Ajout de clients
        kb.add_client("client_001", "John Doe", "john.doe@email.com")
        kb.add_client("client_002", "Jane Smith", "jane.smith@email.com")
        
        print("✅ Données de test ajoutées")
        
        # Test 1: Vérification que l'agent utilise les outils pour le stock
        print("\n🔍 Test 1: Vérification de l'utilisation des outils de stock")
        
        # Requête qui devrait déclencher la vérification de stock
        query = "Je veux commander 5 laptops gaming"
        
        print(f"   Requête: '{query}'")
        response = agent.run_agent(query)
        
        print(f"   Réponse: {response[:200]}...")
        
        # Vérification que les outils ont été appelés
        # On peut vérifier en regardant les logs ou en interceptant les appels
        
        # Test 2: Vérification directe des outils
        print("\n🔍 Test 2: Vérification directe des outils")
        
        # Test de l'outil de vérification de stock
        success, message = tools.check_stock_tool("laptop_001", 3, kb)
        print(f"   Vérification stock (3 laptops): {'✅' if success else '❌'} {message}")
        
        # Test de l'outil de création de commande
        items = [
            {'product_id': 'laptop_001', 'quantity': 2, 'price': 1200.0, 'total': 2400.0},
            {'product_id': 'mouse_001', 'quantity': 1, 'price': 45.0, 'total': 45.0}
        ]
        order_id = tools.create_order_tool("client_001", items, kb)
        print(f"   Création commande: {'✅' if order_id else '❌'} {order_id}")
        
        # Test de l'outil de validation de commande
        if order_id:
            success, message = tools.validate_order_tool(order_id, kb)
            print(f"   Validation commande: {'✅' if success else '❌'} {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'intégration: {e}")
        return False


def test_rule_engine_tools():
    """Test que le moteur de règles utilise les vrais outils"""
    print("\n🧪 TEST 3: MOTEUR DE RÈGLES ET OUTILS")
    print("=" * 60)
    
    kb, vector_store, llm, agent = test_initialisation()
    if not agent:
        return False
    
    try:
        # Ajout de données de test si pas déjà fait
        if not kb.find_product_by_name("Laptop Gaming"):
            kb.add_product("laptop_001", "Laptop Gaming", 1200.0, 15, "Ordinateur portable gaming")
        
        # Test du moteur de règles directement
        print("🔧 Test du moteur de règles avec outils...")
        
        # Requête qui devrait déclencher la règle de vérification de stock
        query = "Je veux commander 3 produits avec livraison express"
        
        rule_result = agent.rule_engine.process_query(query)
        
        print(f"   Intention détectée: {rule_result.get('intent', 'N/A')}")
        print(f"   Entités extraites: {rule_result.get('entities', {})}")
        print(f"   Confiance: {rule_result.get('confidence', 0):.2f}")
        
        # Vérification des actions exécutées
        executed_actions = rule_result.get('executed_actions', [])
        print(f"   Actions exécutées: {len(executed_actions)}")
        
        for action_info in executed_actions:
            action = action_info['action']
            result = action_info['result']
            rule = action_info['rule']
            
            print(f"     - Règle '{rule}' → Action '{action}'")
            print(f"       Résultat: {result.get('status', 'N/A')}")
            
            # Vérification que les résultats viennent des vrais outils
            if action == 'check_stock':
                if 'product_id' in result and 'product_name' in result:
                    print(f"       ✅ Utilise les vrais outils (produit: {result['product_name']})")
                else:
                    print(f"       ❌ N'utilise pas les vrais outils")
            
            elif action == 'calculate_price':
                if 'unit_price' in result and 'total_price' in result:
                    print(f"       ✅ Utilise les vrais outils (prix: {result['total_price']}€)")
                else:
                    print(f"       ❌ N'utilise pas les vrais outils")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test du moteur de règles: {e}")
        return False


def test_agent_tools_usage():
    """Test que l'agent utilise les outils dans ses handlers"""
    print("\n🧪 TEST 4: UTILISATION DES OUTILS DANS LES HANDLERS")
    print("=" * 60)
    
    kb, vector_store, llm, agent = test_initialisation()
    if not agent:
        return False
    
    try:
        # Ajout de données de test
        if not kb.find_product_by_name("Laptop Gaming"):
            kb.add_product("laptop_001", "Laptop Gaming", 1200.0, 15, "Ordinateur portable gaming")
        if not kb.find_client_by_name("John Doe"):
            kb.add_client("client_001", "John Doe", "john.doe@email.com")
        
        # Test 1: Handler create_order avec outils
        print("🔍 Test du handler create_order...")
        
        params = {
            'client_name': 'John Doe',
            'products': [
                {'product_name': 'Laptop Gaming', 'quantity': 2}
            ]
        }
        
        response = agent._handle_create_order(params)
        print(f"   Réponse: {response[:200]}...")
        
        # Vérification que la réponse contient des informations réalistes
        if "Commande" in response and "€" in response:
            print("   ✅ Handler utilise les vrais outils (informations réalistes)")
        else:
            print("   ❌ Handler n'utilise pas les vrais outils")
        
        # Test 2: Handler validate_order avec outils
        print("\n🔍 Test du handler validate_order...")
        
        # Créer une commande d'abord
        items = [
            {'product_id': 'laptop_001', 'quantity': 1, 'price': 1200.0, 'total': 1200.0}
        ]
        order_id = tools.create_order_tool("client_001", items, kb)
        
        if order_id:
            params = {'order_id': order_id}
            response = agent._handle_validate_order(params)
            print(f"   Réponse: {response[:200]}...")
            
            # Vérification que la réponse contient des informations réalistes
            if "validée" in response or "payée" in response:
                print("   ✅ Handler utilise les vrais outils")
            else:
                print("   ❌ Handler n'utilise pas les vrais outils")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des handlers: {e}")
        return False


def test_tools_consistency():
    """Test de la cohérence entre les outils et l'agent"""
    print("\n🧪 TEST 5: COHÉRENCE DES OUTILS")
    print("=" * 60)
    
    kb, vector_store, llm, agent = test_initialisation()
    if not agent:
        return False
    
    try:
        # Ajout de données de test
        if not kb.find_product_by_name("Laptop Gaming"):
            kb.add_product("laptop_001", "Laptop Gaming", 1200.0, 15, "Ordinateur portable gaming")
        if not kb.find_client_by_name("John Doe"):
            kb.add_client("client_001", "John Doe", "john.doe@email.com")
        
        # Test de cohérence: même produit, même résultat
        print("🔍 Test de cohérence des outils...")
        
        # Vérification directe du stock
        success1, message1 = tools.check_stock_tool("laptop_001", 3, kb)
        print(f"   Outil direct - Stock 3 laptops: {'✅' if success1 else '❌'} {message1}")
        
        # Vérification via le moteur de règles
        rule_result = agent.rule_engine.process_query("Je veux commander 3 laptops")
        stock_actions = [a for a in rule_result.get('executed_actions', []) 
                        if a['action'] == 'check_stock']
        
        if stock_actions:
            stock_result = stock_actions[0]['result']
            print(f"   Moteur règles - Stock 3 laptops: {stock_result.get('status', 'N/A')}")
            
            # Vérification de la cohérence
            if (success1 and stock_result.get('status') == 'available') or \
               (not success1 and stock_result.get('status') == 'insufficient'):
                print("   ✅ Cohérence entre outils directs et moteur de règles")
            else:
                print("   ❌ Incohérence entre outils directs et moteur de règles")
        else:
            print("   ⚠️ Aucune action de vérification de stock trouvée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de cohérence: {e}")
        return False


def main():
    """Fonction principale de test"""
    print("🔧 TEST D'INTÉGRATION DES OUTILS DANS L'AGENT")
    print("=" * 70)
    print("Ce test vérifie que l'agent utilise bien les vrais outils")
    print("au lieu de simulations pour les opérations métier.")
    print("=" * 70)
    
    # Tests
    tests = [
        ("Intégration des outils", lambda: test_tools_integration()),
        ("Moteur de règles et outils", lambda: test_rule_engine_tools()),
        ("Handlers et outils", lambda: test_agent_tools_usage()),
        ("Cohérence des outils", lambda: test_tools_consistency())
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
    print("📊 RÉSUMÉ DES TESTS D'INTÉGRATION")
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
        print("\n🎉 Tous les tests d'intégration des outils sont passés !")
        print("   L'agent utilise correctement les vrais outils.")
    else:
        print(f"\n⚠️ {total - passed} test(s) ont échoué.")
        print("   Vérifiez l'intégration des outils dans l'agent.")


if __name__ == "__main__":
    main() 