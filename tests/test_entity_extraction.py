#!/usr/bin/env python3
"""
Script de test pour les améliorations d'extraction d'entités
Teste les nouveaux patterns regex et l'extraction LLM de fallback
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore
from src.llm_interface import LLMInterface
from src.agent import CognitiveOrderAgent


def test_entity_extraction():
    """Test des améliorations d'extraction d'entités"""
    
    print("🧪 Test des améliorations d'extraction d'entités")
    print("=" * 60)
    
    # Initialisation des composants
    kb = KnowledgeBase()
    vs = VectorStore()
    
    # Test avec et sans LLM
    llm_interface = LLMInterface() if os.getenv('OPENAI_API_KEY') else None
    
    agent = CognitiveOrderAgent(kb, vs, llm_interface)
    
    # Cas de test pour l'extraction d'entités
    test_cases = [
        # Tests de noms de clients
        {
            "query": "Créer une commande pour Jean Dupont",
            "expected": {"client_name": "Jean Dupont", "intent": "create_order"}
        },
        {
            "query": "Le client Marie Martin veut commander 2 ordinateurs",
            "expected": {"client_name": "Marie Martin", "intent": "create_order"}
        },
        {
            "query": "Commande pour Pierre Durand avec 3 souris",
            "expected": {"client_name": "Pierre Durand", "intent": "create_order"}
        },
        
        # Tests de produits et quantités
        {
            "query": "Je veux 5 unités de clavier mécanique",
            "expected": {"intent": "create_order", "products": [{"product_name": "clavier mécanique", "quantity": 5}]}
        },
        {
            "query": "Commander 2 écrans 4K avec 1 unité de support",
            "expected": {"intent": "create_order", "products": [{"product_name": "écrans 4K", "quantity": 2}, {"product_name": "support", "quantity": 1}]}
        },
        {
            "query": "Je veux 3 souris gaming et 2 claviers",
            "expected": {"intent": "create_order", "products": [{"product_name": "souris gaming", "quantity": 3}, {"product_name": "claviers", "quantity": 2}]}
        },
        
        # Tests de montants
        {
            "query": "Payer 150,50 € pour la commande A-123",
            "expected": {"amount": "150,50", "order_id": "A-123", "intent": "process_payment"}
        },
        {
            "query": "Montant de 299.99 euros pour les accessoires",
            "expected": {"amount": "299.99", "intent": "process_payment"}
        },
        
        # Tests d'emails et téléphones
        {
            "query": "Ajouter le client Paul avec email paul@example.com",
            "expected": {"client_name": "Paul", "email": "paul@example.com", "intent": "add_client"}
        },
        {
            "query": "Nouveau client Sophie téléphone 06.12.34.56.78",
            "expected": {"client_name": "Sophie", "phone": "06.12.34.56.78", "intent": "add_client"}
        },
        
        # Tests de recommandations
        {
            "query": "Recommande moi des accessoires pour ordinateur",
            "expected": {"query_text": "accessoires pour ordinateur", "intent": "recommend_products"}
        },
        {
            "query": "Suggère des produits similaires à souris gaming",
            "expected": {"reference_product": "souris gaming", "intent": "recommend_products"}
        },
        
        # Tests de statut
        {
            "query": "Vérifier le statut de la commande A-456",
            "expected": {"order_id": "A-456", "intent": "check_status"}
        },
        {
            "query": "Où en est ma commande ?",
            "expected": {"intent": "check_status"}
        }
    ]
    
    print(f"📋 Test de {len(test_cases)} cas d'extraction d'entités")
    print(f"🤖 LLM disponible: {'Oui' if llm_interface else 'Non'}")
    print()
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected = test_case["expected"]
        
        print(f"🧪 Test {i}/{total_tests}: {query}")
        
        try:
            # Test d'extraction d'intention
            intent = agent._extract_intent(query)
            print(f"  🎯 Intention détectée: {intent}")
            
            # Test d'extraction de paramètres
            params = agent._extract_parameters(query, intent)
            print(f"  📋 Paramètres extraits: {params}")
            
            # Vérification des résultats
            intent_match = intent == expected.get("intent", "unknown")
            
            # Vérification des paramètres clés
            param_matches = 0
            total_expected_params = 0
            
            for key, expected_value in expected.items():
                if key != "intent":
                    total_expected_params += 1
                    if key in params:
                        if key == "products":
                            # Vérification spéciale pour les produits
                            if isinstance(expected_value, list) and isinstance(params[key], list):
                                if len(expected_value) == len(params[key]):
                                    param_matches += 1
                        else:
                            # Vérification simple pour les autres paramètres
                            if str(params[key]).lower() == str(expected_value).lower():
                                param_matches += 1
            
            success_rate = param_matches / max(total_expected_params, 1)
            
            if intent_match and success_rate >= 0.7:
                print(f"  ✅ Succès: Intention correcte, {param_matches}/{total_expected_params} paramètres corrects")
                success_count += 1
            else:
                print(f"  ❌ Échec: Intention {'correcte' if intent_match else 'incorrecte'}, {param_matches}/{total_expected_params} paramètres corrects")
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
        
        print()
    
    # Résultats finaux
    success_rate = success_count / total_tests
    print("=" * 60)
    print(f"📊 Résultats finaux: {success_count}/{total_tests} tests réussis ({success_rate:.1%})")
    
    if success_rate >= 0.8:
        print("🎉 Excellent! L'extraction d'entités fonctionne très bien.")
    elif success_rate >= 0.6:
        print("✅ Bon! L'extraction d'entités fonctionne correctement.")
    else:
        print("⚠️ Amélioration nécessaire pour l'extraction d'entités.")
    
    return success_rate


def test_llm_fallback():
    """Test spécifique de l'extraction LLM de fallback"""
    
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️ Test LLM fallback ignoré (OPENAI_API_KEY non défini)")
        return
    
    print("\n🤖 Test de l'extraction LLM de fallback")
    print("=" * 60)
    
    kb = KnowledgeBase()
    vs = VectorStore()
    llm_interface = LLMInterface()
    agent = CognitiveOrderAgent(kb, vs, llm_interface)
    
    # Cas de test complexes pour LLM
    complex_cases = [
        "Je souhaite commander pour mon ami Thomas qui habite à Lyon, 3 unités de ce super écran 4K que j'ai vu hier",
        "Pouvez-vous ajouter ma collègue Sophie Dubois avec son email sophie.dubois@entreprise.fr et son portable 06 78 90 12 34",
        "J'ai besoin de recommandations pour des accessoires de bureau, quelque chose de moderne et ergonomique",
        "Combien coûte la livraison express pour ma commande du 15 mars dernier ?"
    ]
    
    for i, query in enumerate(complex_cases, 1):
        print(f"🧪 Test LLM {i}: {query}")
        
        try:
            intent = agent._extract_intent(query)
            params = agent._extract_parameters(query, intent)
            
            print(f"  🎯 Intention: {intent}")
            print(f"  📋 Paramètres: {params}")
            
            # Test de l'extraction LLM de fallback
            llm_params = agent._extract_with_llm_fallback(query, intent)
            print(f"  🤖 LLM fallback: {llm_params}")
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
        
        print()


def test_pattern_robustness():
    """Test de robustesse des patterns regex"""
    
    print("\n🔧 Test de robustesse des patterns regex")
    print("=" * 60)
    
    kb = KnowledgeBase()
    vs = VectorStore()
    agent = CognitiveOrderAgent(kb, vs, None)  # Sans LLM pour tester uniquement les patterns
    
    # Tests de variations de texte
    variations = [
        # Variations de noms avec accents
        ("Commande pour François", "François"),
        ("Client José María", "José María"),
        ("Nouveau client André", "André"),
        
        # Variations de quantités
        ("5 unités de clavier", "5"),
        ("3 pièces de souris", "3"),
        ("2 exemplaires d'écran", "2"),
        
        # Variations de montants
        ("150,50 €", "150,50"),
        ("299.99 euros", "299.99"),
        ("Prix 45,00", "45,00"),
        
        # Variations d'emails
        ("email: test@example.com", "test@example.com"),
        ("courriel user.name@domain.co.uk", "user.name@domain.co.uk"),
        
        # Variations de téléphones
        ("06.12.34.56.78", "06.12.34.56.78"),
        ("06 12 34 56 78", "06 12 34 56 78"),
        ("06-12-34-56-78", "06-12-34-56-78")
    ]
    
    success_count = 0
    total_tests = len(variations)
    
    for query, expected in variations:
        print(f"🧪 Test: {query}")
        
        try:
            # Test avec les patterns d'entités
            found = False
            for param_name, patterns in agent.entity_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, query, re.IGNORECASE)
                    if match:
                        value = match.group(1).strip()
                        if value.lower() == expected.lower():
                            print(f"  ✅ Trouvé: {param_name} = {value}")
                            found = True
                            success_count += 1
                            break
                if found:
                    break
            
            if not found:
                print(f"  ❌ Non trouvé: attendu {expected}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
        
        print()
    
    success_rate = success_count / total_tests
    print(f"📊 Robustesse des patterns: {success_count}/{total_tests} ({success_rate:.1%})")
    
    return success_rate


if __name__ == "__main__":
    print("🚀 Démarrage des tests d'extraction d'entités améliorées")
    print()
    
    # Test principal d'extraction d'entités
    main_success = test_entity_extraction()
    
    # Test de robustesse des patterns
    pattern_success = test_pattern_robustness()
    
    # Test LLM fallback
    test_llm_fallback()
    
    print("\n" + "=" * 60)
    print("📋 Résumé des tests")
    print(f"  • Extraction d'entités: {main_success:.1%}")
    print(f"  • Robustesse des patterns: {pattern_success:.1%}")
    print(f"  • LLM fallback: {'Testé' if os.getenv('OPENAI_API_KEY') else 'Non testé'}")
    
    if main_success >= 0.7 and pattern_success >= 0.8:
        print("\n🎉 Tous les tests sont satisfaisants!")
    else:
        print("\n⚠️ Certains tests nécessitent des améliorations.") 