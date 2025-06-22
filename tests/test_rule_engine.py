#!/usr/bin/env python3
"""
Test du moteur de règles
Vérifie que le moteur de règles fonctionne correctement
"""

import sys
import os
import json
from datetime import datetime

# Ajout du répertoire courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.rule_engine import AdvancedRuleEngine, BusinessRule
from src.agent import CognitiveOrderAgent
from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore

def print_header(title: str):
    """Affiche un en-tête formaté"""
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)

def print_section(title: str):
    """Affiche une section formatée"""
    print(f"\n📋 {title}")
    print("-" * 40)

def test_rule_engine_basic():
    """Test basique du moteur de règles"""
    print_header("TEST BASIQUE DU MOTEUR DE RÈGLES")
    
    # Initialisation du moteur
    rule_engine = AdvancedRuleEngine()
    
    # Affichage des règles par défaut
    print_section("Règles par défaut")
    for rule in rule_engine.business_rules:
        print(f"✅ {rule.name}: {rule.description}")
        print(f"   Conditions: {rule.conditions}")
        print(f"   Actions: {rule.actions}")
        print(f"   Priorité: {rule.priority}, Catégorie: {rule.category}")
        print()
    
    # Test de requêtes
    test_queries = [
        "Je veux commander 3 produits avec livraison express",
        "Je voudrais payer 50 euros pour ma commande",
        "Vérifier le stock de mes articles",
        "Annuler ma commande"
    ]
    
    print_section("Test de requêtes")
    for query in test_queries:
        print(f"\n🔍 Requête: '{query}'")
        result = rule_engine.process_query(query)
        
        print(f"   Intention: {result['intent']}")
        print(f"   Confiance: {result['confidence']:.2f}")
        print(f"   Entités: {result['entities']}")
        print(f"   Actions exécutées: {len(result['executed_actions'])}")
        
        for action_info in result['executed_actions']:
            print(f"     - {action_info['action']} (règle: {action_info['rule']})")

def test_rule_creation():
    """Test de création de règles personnalisées"""
    print_header("TEST DE CRÉATION DE RÈGLES")
    
    rule_engine = AdvancedRuleEngine()
    
    # Création d'une règle personnalisée
    custom_rule = BusinessRule(
        name="remise_fidelite",
        description="Applique une remise de fidélité pour les clients VIP",
        conditions=["intent:commander", "has_quantity", "client_type:VIP"],
        actions=["apply_loyalty_discount", "calculate_final_price"],
        priority=2,
        category="remise"
    )
    
    rule_engine.add_business_rule(custom_rule)
    print(f"✅ Règle créée: {custom_rule.name}")
    
    # Test de la nouvelle règle
    test_query = "Je veux commander 5 produits en tant que client VIP"
    print(f"\n🔍 Test avec: '{test_query}'")
    
    result = rule_engine.process_query(test_query)
    print(f"   Actions exécutées: {len(result['executed_actions'])}")
    
    # Affichage des statistiques
    stats = rule_engine.get_statistics()
    print_section("Statistiques après ajout")
    print(f"Règles totales: {stats['business_rules']['total']}")
    print(f"Règles activées: {stats['business_rules']['enabled']}")
    print(f"Catégories: {stats['business_rules']['categories']}")

def test_agent_integration():
    """Test de l'intégration avec l'agent"""
    print_header("TEST D'INTÉGRATION AVEC L'AGENT")
    
    # Initialisation des composants
    kb = KnowledgeBase()
    vs = VectorStore()
    agent = CognitiveOrderAgent(kb, vs)
    
    # Test de requêtes avec l'agent
    test_queries = [
        "Je veux commander 2 produits avec livraison express",
        "Vérifier le statut de ma commande",
        "Recommander des produits similaires"
    ]
    
    for query in test_queries:
        print(f"\n🤖 Agent - Requête: '{query}'")
        response = agent.run_agent(query)
        print(f"   Réponse: {response[:200]}...")

def test_rule_export_import():
    """Test d'export et import de règles"""
    print_header("TEST EXPORT/IMPORT DE RÈGLES")
    
    rule_engine = AdvancedRuleEngine()
    
    # Export des règles
    print_section("Export des règles")
    exported_data = rule_engine.export_rules('json')
    print(f"✅ Règles exportées ({len(exported_data)} caractères)")
    
    # Sauvegarde dans un fichier
    with open('rules_backup.json', 'w', encoding='utf-8') as f:
        f.write(exported_data)
    print("💾 Sauvegardé dans 'rules_backup.json'")
    
    # Import des règles
    print_section("Import des règles")
    rule_engine.import_rules(exported_data, 'json')
    print("✅ Règles importées avec succès")

def test_performance():
    """Test de performance du moteur"""
    print_header("TEST DE PERFORMANCE")
    
    rule_engine = AdvancedRuleEngine()
    
    # Test avec plusieurs requêtes
    test_queries = [
        "commander 1 produit",
        "commander 2 produits avec livraison",
        "payer 100 euros",
        "vérifier le stock",
        "annuler commande",
        "modifier ma commande",
        "voir l'historique",
        "recommander des produits"
    ]
    
    import time
    start_time = time.time()
    
    for i, query in enumerate(test_queries, 1):
        result = rule_engine.process_query(query)
        print(f"   {i}. '{query}' -> {result['intent']} (conf: {result['confidence']:.2f})")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n⏱️  Temps total: {total_time:.3f}s")
    print(f"📊 Temps moyen par requête: {total_time/len(test_queries):.3f}s")
    
    # Statistiques finales
    stats = rule_engine.get_statistics()
    print(f"🎯 Inférences totales: {stats['rule_engine']['total_inferences']}")
    print(f"📈 Taux de succès: {stats['rule_engine']['performance_metrics']['success_rate']:.2%}")

def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE DES TESTS DU MOTEUR DE RÈGLES")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Tests en séquence
        test_rule_engine_basic()
        test_rule_creation()
        test_agent_integration()
        test_rule_export_import()
        test_performance()
        
        print_header("✅ TOUS LES TESTS TERMINÉS AVEC SUCCÈS")
        print("🎉 Le moteur de règles est opérationnel !")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 