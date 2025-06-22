#!/usr/bin/env python3
"""
Test de l'exemple médical
Vérifie que l'exemple médical fonctionne correctement
"""

import sys
import os
import json
import yaml
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import des modules du système
from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore
from src.llm_assistants import LLMAssistant

import requests
import time

# Configuration
API_BASE_URL = "http://localhost:5001"

def test_medical_workflow():
    """Teste la génération de workflow médical"""
    print("🏥 Test de génération de workflow médical...")
    
    workflow_data = {
        "domain": "healthcare",
        "business_context": """
        Système de gestion de consultations médicales avec :
        - Prise de rendez-vous patients
        - Validation des dossiers médicaux
        - Conduite de consultations
        - Mise à jour des dossiers
        - Prescription de médicaments
        - Suivi des traitements
        """
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/llm/generate_workflow",
            json=workflow_data,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['success']:
            print("✅ Workflow médical généré avec succès")
            print(f"   Nombre d'étapes: {len(data['workflow'])}")
            print("\n📋 Étapes du workflow:")
            for i, step in enumerate(data['workflow'], 1):
                print(f"   {i}. {step.get('action', 'N/A')}")
                print(f"      Description: {step.get('description', 'N/A')}")
                print(f"      Paramètres: {', '.join(step.get('params', []))}")
                print()
        else:
            print(f"❌ Erreur: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_medical_patterns():
    """Teste la génération de patterns d'extraction médicaux"""
    print("\n🔍 Test de génération de patterns médicaux...")
    
    pattern_data = {
        "entity_type": "Patient",
        "sample_data": """
        Nom: Marie Dupont
        Date de naissance: 15/03/1985
        Numéro de sécurité sociale: 185031512345678
        Téléphone: +33 1 23 45 67 89
        Email: marie.dupont@email.com
        Adresse: 123 Rue de la Santé, 75001 Paris
        Groupe sanguin: A+
        Allergies: Pénicilline, Pollen
        Antécédents: Hypertension, Diabète type 2
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
            print("✅ Patterns médicaux générés avec succès")
            print(f"   Nombre de patterns: {len(data['patterns'])}")
            print("\n🔍 Patterns d'extraction:")
            for i, pattern in enumerate(data['patterns'], 1):
                print(f"   {i}. {pattern.get('name', 'N/A')}")
                print(f"      Description: {pattern.get('description', 'N/A')}")
                print(f"      Patterns: {pattern.get('patterns', [])}")
                print(f"      Exemples: {pattern.get('examples', [])}")
                print()
        else:
            print(f"❌ Erreur: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_medical_rules():
    """Teste la génération de règles métier médicales"""
    print("\n📋 Test de génération de règles médicales...")
    
    rule_data = {
        "business_scenario": """
        Gestion des consultations médicales avec validation automatique des prescriptions
        et suivi des protocoles de sécurité médicale
        """,
        "constraints": [
            "Les patients mineurs nécessitent l'autorisation parentale",
            "Les prescriptions de médicaments contrôlés nécessitent une validation spéciale",
            "Les patients avec allergies doivent être signalés avant toute prescription",
            "Les consultations d'urgence ont priorité sur les consultations programmées",
            "Les dossiers médicaux doivent être mis à jour après chaque consultation"
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
            print("✅ Règles médicales générées avec succès")
            print(f"   Nombre de règles: {len(data['rules'])}")
            print("\n⚖️ Règles métier:")
            for i, rule in enumerate(data['rules'], 1):
                print(f"   {i}. {rule.get('name', 'N/A')}")
                print(f"      Condition: {rule.get('condition', 'N/A')}")
                print(f"      Action: {rule.get('action', 'N/A')}")
                print(f"      Description: {rule.get('description', 'N/A')}")
                print(f"      Priorité: {rule.get('priority', 'N/A')}")
                print()
        else:
            print(f"❌ Erreur: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_medical_templates():
    """Teste la récupération des templates médicaux"""
    print("\n📝 Test de récupération des templates médicaux...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/llm/assistants/templates")
        data = response.json()
        
        if data['success']:
            print("✅ Templates récupérés avec succès")
            templates = data['templates']
            
            if 'workflow_templates' in templates:
                print(f"   Templates de workflow: {len(templates['workflow_templates'])}")
                for template in templates['workflow_templates']:
                    print(f"      - {template}")
            
            if 'pattern_templates' in templates:
                print(f"   Templates de patterns: {len(templates['pattern_templates'])}")
                for template in templates['pattern_templates']:
                    print(f"      - {template}")
            
            if 'rule_templates' in templates:
                print(f"   Templates de règles: {len(templates['rule_templates'])}")
                for template in templates['rule_templates']:
                    print(f"      - {template}")
        else:
            print(f"❌ Erreur: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_medical_validation():
    """Teste la validation de contenu médical"""
    print("\n✅ Test de validation de contenu médical...")
    
    test_content = {
        "output_type": "workflow",
        "content": {
            "steps": [
                {
                    "action": "validate_patient",
                    "description": "Validation du dossier patient",
                    "params": ["patient_id"]
                },
                {
                    "action": "check_appointment",
                    "description": "Vérification du rendez-vous",
                    "params": ["appointment_id"]
                },
                {
                    "action": "conduct_consultation",
                    "description": "Conduite de la consultation médicale",
                    "params": ["patient_data", "consultation_type"]
                }
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
                print(f"   Erreurs: {validation['errors']}")
            if 'warnings' in validation and validation['warnings']:
                print(f"   Avertissements: {validation['warnings']}")
        else:
            print(f"❌ Erreur de validation: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def test_medical_configuration():
    """Teste la configuration pour le domaine médical"""
    print("\n🔧 Test de configuration médicale...")
    
    config = {
        "api_key": "test-medical-key",
        "model": "gpt-4",
        "temperature": 0.3  # Plus conservateur pour le médical
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/llm/assistants/configure",
            json=config,
            headers={'Content-Type': 'application/json'}
        )
        data = response.json()
        
        if data['success']:
            print("✅ Configuration médicale réussie")
            print("   Modèle configuré pour la précision médicale")
        else:
            print(f"❌ Erreur de configuration: {data.get('error', 'Erreur inconnue')}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

def main():
    """Fonction principale de test médical"""
    print("🏥 Test des Assistants LLM - Domaine Médical")
    print("=" * 60)
    
    # Attendre que l'API soit prête
    print("⏳ Attente du démarrage de l'API...")
    time.sleep(2)
    
    # Tests séquentiels
    test_medical_configuration()
    test_medical_workflow()
    test_medical_patterns()
    test_medical_rules()
    test_medical_templates()
    test_medical_validation()
    
    print("\n" + "=" * 60)
    print("✅ Tests médicaux terminés")
    print("\n💡 Résultats attendus:")
    print("   - Workflow: Étapes de consultation médicale")
    print("   - Patterns: Extraction de données patient")
    print("   - Règles: Validation et sécurité médicale")
    print("   - Templates: Modèles spécifiques au domaine médical")

if __name__ == "__main__":
    main() 