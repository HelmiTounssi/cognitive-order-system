#!/usr/bin/env python3
"""
Test de l'API d'import
Vérifie que l'import de configurations fonctionne correctement
"""

import sys
import os
import json
import yaml
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config_manager import ConfigurationManager
import requests
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:5001"
EXAMPLES_DIR = Path("examples")

def test_api_health():
    """Test de la santé de l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API accessible")
            return True
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion à l'API: {e}")
        return False

def test_import_configuration(yaml_file: Path):
    """Test l'import d'une configuration YAML"""
    print(f"\n📥 Test d'import: {yaml_file.name}")
    
    try:
        # Lecture du fichier YAML
        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
        
        print(f"   📄 Contenu lu: {len(yaml_content)} caractères")
        
        # Import via l'API
        with open(yaml_file, 'rb') as f:
            files = {'file': (yaml_file.name, f, 'application/x-yaml')}
            response = requests.post(f"{API_BASE_URL}/api/configurations/import", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Import réussi: {result.get('message', '')}")
            print(f"   📋 Nom: {result.get('config_name', 'N/A')}")
            print(f"   🏷️ Version: {result.get('version', 'N/A')}")
            return True
        else:
            print(f"   ❌ Erreur d'import: {response.status_code}")
            print(f"   📝 Détails: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur lors de l'import: {e}")
        return False

def test_rules_after_import():
    """Test la récupération des règles après import"""
    print("\n🔍 Vérification des règles importées")
    
    try:
        # Récupération des règles
        response = requests.get(f"{API_BASE_URL}/api/rules")
        
        if response.status_code == 200:
            result = response.json()
            rules = result.get('rules', [])
            print(f"   📋 Règles trouvées: {len(rules)}")
            
            for rule in rules[:3]:  # Afficher les 3 premières règles
                print(f"      - {rule.get('name', 'N/A')} ({rule.get('category', 'N/A')})")
            
            if len(rules) > 3:
                print(f"      ... et {len(rules) - 3} autres")
            
            return len(rules) > 0
        else:
            print(f"   ❌ Erreur lors de la récupération des règles: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_ontology_after_import():
    """Test la récupération de l'ontologie après import"""
    print("\n🧠 Vérification de l'ontologie importée")
    
    try:
        # Récupération des entités
        response = requests.get(f"{API_BASE_URL}/api/ontology/entities")
        
        if response.status_code == 200:
            result = response.json()
            entities = result.get('entities', [])
            print(f"   📋 Entités trouvées: {len(entities)}")
            
            for entity in entities[:3]:  # Afficher les 3 premières entités
                properties = entity.get('properties', [])
                print(f"      - {entity.get('name', 'N/A')} ({len(properties)} propriétés)")
            
            if len(entities) > 3:
                print(f"      ... et {len(entities) - 3} autres")
            
            return len(entities) > 0
        else:
            print(f"   ❌ Erreur lors de la récupération de l'ontologie: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def test_rule_engine_statistics():
    """Test les statistiques du moteur de règles"""
    print("\n📊 Statistiques du moteur de règles")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/rules/statistics")
        
        if response.status_code == 200:
            result = response.json()
            stats = result.get('statistics', {})
            business_rules = stats.get('business_rules', {})
            
            print(f"   📋 Règles totales: {business_rules.get('total', 0)}")
            print(f"   ✅ Règles activées: {business_rules.get('enabled', 0)}")
            print(f"   🏷️ Catégories: {business_rules.get('categories', {})}")
            
            return True
        else:
            print(f"   ❌ Erreur lors de la récupération des statistiques: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Test d'Import via l'API")
    print("=" * 50)
    
    # Test de la santé de l'API
    if not test_api_health():
        print("\n❌ L'API n'est pas accessible. Assurez-vous qu'elle est démarrée.")
        return
    
    # Recherche des fichiers YAML
    yaml_files = list(EXAMPLES_DIR.glob("*.yaml"))
    if not yaml_files:
        print(f"\n❌ Aucun fichier YAML trouvé dans {EXAMPLES_DIR}")
        return
    
    print(f"\n📁 Fichiers YAML trouvés: {len(yaml_files)}")
    
    # Test d'import de chaque fichier
    successful_imports = 0
    for yaml_file in yaml_files:
        if test_import_configuration(yaml_file):
            successful_imports += 1
    
    print(f"\n📊 Résumé des imports: {successful_imports}/{len(yaml_files)} réussis")
    
    if successful_imports > 0:
        # Vérification des données importées
        print("\n🔍 Vérification des données importées...")
        
        # Attendre un peu pour que l'import soit traité
        time.sleep(2)
        
        rules_ok = test_rules_after_import()
        ontology_ok = test_ontology_after_import()
        stats_ok = test_rule_engine_statistics()
        
        print(f"\n📋 Résumé de la vérification:")
        print(f"   ✅ Règles: {'OK' if rules_ok else '❌'}")
        print(f"   🧠 Ontologie: {'OK' if ontology_ok else '❌'}")
        print(f"   📊 Statistiques: {'OK' if stats_ok else '❌'}")
        
        if rules_ok and ontology_ok:
            print("\n🎉 Import et vérification réussis !")
            print("\n🌐 Vous pouvez maintenant:")
            print("   1. Aller sur l'interface web (http://localhost:5173)")
            print("   2. Vérifier les onglets 'Règles' et 'Ontologie'")
            print("   3. Tester les fonctionnalités importées")
        else:
            print("\n⚠️ Import partiel - certaines données n'ont pas été importées correctement")
    else:
        print("\n❌ Aucun import réussi")

if __name__ == "__main__":
    main() 