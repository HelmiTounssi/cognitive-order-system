#!/usr/bin/env python3
"""
Test du gestionnaire de configuration
Vérifie que la gestion des configurations fonctionne correctement
"""

import sys
import os
import json
import yaml
import tempfile
from pathlib import Path
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import ConfigurationManager
from src.core.rule_engine import AdvancedRuleEngine, BusinessRule
from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore


def create_test_configuration():
    """Crée une configuration de test complète"""
    
    print("🔧 Création d'une configuration de test...")
    
    # Création des instances
    rule_engine = AdvancedRuleEngine()
    knowledge_base = KnowledgeBase()
    vector_store = VectorStore()
    
    # Ajout de règles de test
    rule1 = BusinessRule(
        name="Règle Commande Express",
        description="Gestion des commandes express avec livraison prioritaire",
        conditions={
            "intent": "commander",
            "delivery_type": "express",
            "amount": {"operator": ">=", "value": 50}
        },
        actions=[
            {"action": "check_stock", "params": {"product_id": "{product_id}"}},
            {"action": "process_payment", "params": {"amount": "{amount}"}},
            {"action": "schedule_delivery", "params": {"type": "express"}}
        ],
        priority=1,
        category="commande"
    )
    
    rule2 = BusinessRule(
        name="Règle Remise Fidélité",
        description="Application de remise pour clients fidèles",
        conditions={
            "intent": "commander",
            "customer_type": "fidèle",
            "amount": {"operator": ">=", "value": 100}
        },
        actions=[
            {"action": "apply_discount", "params": {"percentage": 10}},
            {"action": "process_payment", "params": {"amount": "{amount_with_discount}"}}
        ],
        priority=2,
        category="fidélité"
    )
    
    rule_engine.add_business_rule(rule1)
    rule_engine.add_business_rule(rule2)
    
    # Configuration LLM
    llm_config = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "api_key_configured": True
    }
    
    # Configuration des outils
    tools_config = {
        "stock_api": {
            "enabled": True,
            "endpoint": "http://localhost:5001/api/tools/stock",
            "timeout": 30
        },
        "payment_api": {
            "enabled": True,
            "endpoint": "http://localhost:5001/api/tools/payment",
            "timeout": 60
        },
        "delivery_api": {
            "enabled": True,
            "endpoint": "http://localhost:5001/api/tools/delivery",
            "timeout": 45
        }
    }
    
    # Configuration de l'agent
    agent_config = {
        "intent_patterns": {
            "commander": ["commander", "acheter", "passer commande"],
            "consulter": ["consulter", "voir", "afficher"],
            "annuler": ["annuler", "supprimer", "retirer"]
        },
        "fallback_enabled": True,
        "confidence_threshold": 0.7,
        "max_actions_per_query": 5
    }
    
    return rule_engine, knowledge_base, vector_store, llm_config, tools_config, agent_config


def test_export_configuration():
    """Test de l'export de configuration"""
    
    print("\n📤 Test d'export de configuration...")
    
    # Création du gestionnaire
    config_manager = ConfigurationManager("test_configs")
    
    # Création de la configuration de test
    rule_engine, kb, vs, llm_config, tools_config, agent_config = create_test_configuration()
    
    try:
        # Export en JSON
        json_file = config_manager.export_configuration(
            rule_engine=rule_engine,
            knowledge_base=kb,
            vector_store=vs,
            llm_config=llm_config,
            tools_config=tools_config,
            agent_config=agent_config,
            format='json',
            filename='test_config_complete.json'
        )
        print(f"✅ Configuration exportée en JSON: {json_file}")
        
        # Export en YAML
        yaml_file = config_manager.export_configuration(
            rule_engine=rule_engine,
            knowledge_base=kb,
            vector_store=vs,
            llm_config=llm_config,
            tools_config=tools_config,
            agent_config=agent_config,
            format='yaml',
            filename='test_config_complete.yaml'
        )
        print(f"✅ Configuration exportée en YAML: {yaml_file}")
        
        return json_file, yaml_file
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        return None, None


def test_import_configuration(json_file, yaml_file):
    """Test de l'import de configuration"""
    
    print("\n📥 Test d'import de configuration...")
    
    config_manager = ConfigurationManager("test_configs")
    
    try:
        # Import depuis JSON
        print("Import depuis JSON...")
        json_config = config_manager.import_configuration(json_file)
        print(f"✅ Configuration JSON importée: {json_config['name']}")
        print(f"   Version: {json_config['version']}")
        print(f"   Règles: {len(json_config['rule_engine']['business_rules'])}")
        
        # Import depuis YAML
        print("Import depuis YAML...")
        yaml_config = config_manager.import_configuration(yaml_file)
        print(f"✅ Configuration YAML importée: {yaml_config['name']}")
        print(f"   Version: {yaml_config['version']}")
        print(f"   Règles: {len(yaml_config['rule_engine']['business_rules'])}")
        
        return json_config, yaml_config
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        return None, None


def test_apply_configuration(json_config, yaml_config):
    """Test de l'application de configuration"""
    
    print("\n🔧 Test d'application de configuration...")
    
    config_manager = ConfigurationManager("test_configs")
    
    # Création d'instances vides
    rule_engine = AdvancedRuleEngine()
    knowledge_base = KnowledgeBase()
    vector_store = VectorStore()
    
    try:
        # Application de la configuration JSON
        print("Application de la configuration JSON...")
        success = config_manager.apply_configuration(json_config, rule_engine, knowledge_base, vector_store)
        
        if success:
            print(f"✅ Configuration JSON appliquée avec succès")
            print(f"   Règles chargées: {len(rule_engine.business_rules)}")
            
            # Affichage des règles appliquées
            for rule in rule_engine.business_rules:
                print(f"   - {rule.name} ({rule.category})")
        else:
            print("❌ Erreur lors de l'application de la configuration JSON")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'application: {e}")


def test_list_configurations():
    """Test de la liste des configurations"""
    
    print("\n📋 Test de la liste des configurations...")
    
    config_manager = ConfigurationManager("test_configs")
    
    try:
        configs = config_manager.list_configurations()
        print(f"✅ Configurations trouvées: {len(configs)}")
        
        for config in configs:
            print(f"   📄 {config['filename']}")
            print(f"      Nom: {config['name']}")
            print(f"      Format: {config['format']}")
            print(f"      Taille: {config['size']} bytes")
            print(f"      Modifié: {config['updated_at']}")
            print()
            
    except Exception as e:
        print(f"❌ Erreur lors de la liste: {e}")


def create_sample_configurations():
    """Crée des configurations d'exemple pour démonstration"""
    
    print("\n🎨 Création de configurations d'exemple...")
    
    config_manager = ConfigurationManager("test_configs")
    
    # Configuration e-commerce
    ecommerce_config = {
        "name": "Configuration E-commerce Standard",
        "description": "Configuration complète pour un site e-commerce",
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "rule_engine": {
            "business_rules": [
                {
                    "name": "Gestion Stock",
                    "description": "Vérification automatique du stock",
                    "conditions": {"intent": "commander"},
                    "actions": [{"action": "check_stock"}],
                    "priority": 1,
                    "category": "stock",
                    "enabled": True
                }
            ],
            "statistics": {"total_rules": 1, "active_rules": 1},
            "templates": {}
        },
        "knowledge_base": {
            "ontology_classes": [
                {"name": "Product", "properties": ["name", "price", "stock"]},
                {"name": "Order", "properties": ["items", "total", "status"]}
            ],
            "instances": [],
            "business_handlers": []
        },
        "vector_store": {
            "collections": ["products", "orders"],
            "statistics": {"total_vectors": 0}
        },
        "llm_config": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        "tools_config": {
            "stock_api": {"enabled": True},
            "payment_api": {"enabled": True},
            "delivery_api": {"enabled": True}
        },
        "agent_config": {
            "intent_patterns": {"commander": ["commander", "acheter"]},
            "fallback_enabled": True,
            "confidence_threshold": 0.7
        },
        "metadata": {
            "exported_by": "ConfigurationManager",
            "system_version": "1.0.0",
            "business_domain": "e-commerce"
        }
    }
    
    # Sauvegarde en JSON
    json_file = config_manager.config_dir / "ecommerce_config.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(ecommerce_config, f, indent=2, ensure_ascii=False)
    
    # Sauvegarde en YAML
    yaml_file = config_manager.config_dir / "ecommerce_config.yaml"
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(ecommerce_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Configuration e-commerce créée: {json_file}")
    print(f"✅ Configuration e-commerce créée: {yaml_file}")


def main():
    """Fonction principale de test"""
    
    print("🧪 Test du Gestionnaire de Configuration")
    print("=" * 50)
    
    # Création de configurations d'exemple
    create_sample_configurations()
    
    # Test d'export
    json_file, yaml_file = test_export_configuration()
    
    if json_file and yaml_file:
        # Test d'import
        json_config, yaml_config = test_import_configuration(json_file, yaml_file)
        
        if json_config and yaml_config:
            # Test d'application
            test_apply_configuration(json_config, yaml_config)
    
    # Test de la liste
    test_list_configurations()
    
    print("\n🎉 Tests terminés!")
    print("\n📁 Les configurations sont disponibles dans le dossier 'test_configs'")
    print("🌐 Vous pouvez maintenant tester l'interface d'administration:")
    print("   1. Démarrez l'API: python admin_api.py")
    print("   2. Démarrez le frontend: cd admin-frontend && npm run dev")
    print("   3. Allez sur l'onglet 'Configurations' pour tester l'import/export")


if __name__ == "__main__":
    main() 