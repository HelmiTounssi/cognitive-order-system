#!/usr/bin/env python3
"""
Test des assistants LLM
Vérifie que les assistants LLM fonctionnent correctement
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm_assistants import LLMAssistant, WorkflowGenerator, PatternGenerator, RuleGenerator
import requests
import time

# Configuration
API_BASE_URL = "http://localhost:5001"

def test_assistants_status():
    """Teste le statut des assistants LLM"""
    print("🔍 Test du statut des assistants LLM...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/llm/assistants/status")
        data = response.json()
        
        if data['success']:
            print("✅ Statut des assistants récupéré avec succès:")
            for assistant, status in data['status'].items():
                status_icon = "🟢" if status else "🔴"
                print(f"   {status_icon} {assistant}: {'Disponible' if status else 'Non disponible'}")
        else:
            print(f"❌ Erreur: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_assistants_configuration():
    """Teste la configuration des assistants LLM"""
    print("\n🔧 Test de la configuration des assistants...")
    
    # Configuration de test (sans clé API réelle)
    config = {
        "api_key": "test-key",
        "model": "gpt-4",
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/llm/assistants/configure",
            json=config,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['success']:
            print("✅ Configuration des assistants réussie")
        else:
            print(f"❌ Erreur de configuration: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_workflow_generation():
    """Teste la génération de workflow"""
    print("\n🔄 Test de génération de workflow...")
    
    workflow_data = {
        "domain": "e-commerce",
        "business_context": "Système de gestion de commandes en ligne avec gestion des stocks, paiements et livraisons"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/llm/generate_workflow",
            json=workflow_data,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['success']:
            print("✅ Workflow généré avec succès")
            print(f"   Nombre d'étapes: {len(data['workflow'])}")
            for i, step in enumerate(data['workflow'][:3]):  # Affiche les 3 premières étapes
                print(f"   Étape {i+1}: {step.get('action', 'N/A')}")
            if len(data['workflow']) > 3:
                print(f"   ... et {len(data['workflow']) - 3} autres étapes")
        else:
            print(f"❌ Erreur de génération: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_pattern_generation():
    """Teste la génération de patterns d'extraction"""
    print("\n🔍 Test de génération de patterns...")
    
    pattern_data = {
        "entity_type": "Client",
        "sample_data": """
        Nom: Jean Dupont
        Email: jean.dupont@email.com
        Téléphone: +33 1 23 45 67 89
        Adresse: 123 Rue de la Paix, 75001 Paris
        """
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/llm/generate_patterns",
            json=pattern_data,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['success']:
            print("✅ Patterns générés avec succès")
            print(f"   Nombre de patterns: {len(data['patterns'])}")
            for i, pattern in enumerate(data['patterns'][:2]):  # Affiche les 2 premiers patterns
                print(f"   Pattern {i+1}: {pattern.get('name', 'N/A')}")
            if len(data['patterns']) > 2:
                print(f"   ... et {len(data['patterns']) - 2} autres patterns")
        else:
            print(f"❌ Erreur de génération: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_rule_generation():
    """Teste la génération de règles métier"""
    print("\n📋 Test de génération de règles...")
    
    rule_data = {
        "business_scenario": "Gestion des commandes avec validation automatique",
        "constraints": [
            "Les commandes de plus de 1000€ nécessitent une validation manuelle",
            "Les produits en rupture de stock ne peuvent pas être commandés",
            "Les clients avec un historique de paiement négatif sont limités à 100€"
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/llm/generate_rules",
            json=rule_data,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['success']:
            print("✅ Règles générées avec succès")
            print(f"   Nombre de règles: {len(data['rules'])}")
            for i, rule in enumerate(data['rules'][:2]):  # Affiche les 2 premières règles
                print(f"   Règle {i+1}: {rule.get('name', 'N/A')}")
            if len(data['rules']) > 2:
                print(f"   ... et {len(data['rules']) - 2} autres règles")
        else:
            print(f"❌ Erreur de génération: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_templates():
    """Teste la récupération des templates"""
    print("\n📝 Test de récupération des templates...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/llm/assistants/templates")
        data = response.json()
        
        if data['success']:
            print("✅ Templates récupérés avec succès")
            templates = data['templates']
            for template_type, template_list in templates.items():
                print(f"   {template_type}: {len(template_list)} templates disponibles")
        else:
            print(f"❌ Erreur: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_validation():
    """Teste la validation de sortie"""
    print("\n✅ Test de validation de sortie...")
    
    test_content = {
        "output_type": "workflow",
        "content": {
            "steps": [
                {"action": "validate_order", "description": "Valider la commande"}
            ]
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/llm/assistants/validate",
            json=test_content,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['success']:
            print("✅ Validation réussie")
            validation = data['validation']
            print(f"   Valide: {validation.get('is_valid', 'N/A')}")
            if 'errors' in validation and validation['errors']:
                print(f"   Erreurs: {len(validation['errors'])}")
        else:
            print(f"❌ Erreur de validation: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 Test des Assistants LLM")
    print("=" * 50)
    
    # Tests séquentiels
    test_assistants_status()
    test_assistants_configuration()
    test_workflow_generation()
    test_pattern_generation()
    test_rule_generation()
    test_templates()
    test_validation()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés")
    print("\n💡 Pour tester avec une vraie clé API OpenAI:")
    print("   1. Configurez votre clé API dans l'interface web")
    print("   2. Ou modifiez ce script avec votre clé API")
    print("   3. Relancez les tests")

if __name__ == "__main__":
    main() 