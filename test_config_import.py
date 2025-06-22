#!/usr/bin/env python3
"""
Script de test pour l'import de configuration
Diagnostique les erreurs d'import de configuration
"""

import sys
import os
import requests
import yaml
import json

# Ajouter la racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

def test_simple_config():
    """Teste un import de configuration simple"""
    print("🔍 Test d'import de configuration simple...")
    
    config = {
        'name': 'Test Config',
        'version': '1.0',
        'description': 'Configuration de test'
    }
    
    try:
        files = {'file': ('test_simple.yaml', yaml.dump(config), 'application/x-yaml')}
        response = requests.post('http://localhost:5000/api/configurations/import', files=files)
        
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            print("  ✅ Import simple réussi")
            return True
        else:
            print("  ❌ Import simple échoué")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def test_complete_config():
    """Teste un import de configuration complète"""
    print("\n🔍 Test d'import de configuration complète...")
    
    config = {
        'name': 'Configuration Complète',
        'version': '1.0',
        'description': 'Configuration complète de test',
        'business_rules': [
            {
                'name': 'Règle Test',
                'description': 'Règle de test',
                'conditions': ['intent:test'],
                'actions': ['test_action'],
                'priority': 1,
                'category': 'test'
            }
        ],
        'ontology_classes': [
            {
                'name': 'TestClass',
                'description': 'Classe de test',
                'properties': [
                    {
                        'name': 'test_property',
                        'type': 'string',
                        'description': 'Propriété de test'
                    }
                ]
            }
        ],
        'vector_store_collections': [
            {
                'name': 'test_collection',
                'description': 'Collection de test'
            }
        ],
        'llm_config': {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7
        },
        'tools_config': {
            'enabled_tools': ['test_tool']
        },
        'agent_config': {
            'name': 'TestAgent',
            'description': 'Agent de test'
        }
    }
    
    try:
        files = {'file': ('test_complete.yaml', yaml.dump(config, default_flow_style=False), 'application/x-yaml')}
        response = requests.post('http://localhost:5000/api/configurations/import', files=files)
        
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            print("  ✅ Import complet réussi")
            return True
        else:
            print("  ❌ Import complet échoué")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def test_file_import():
    """Teste l'import d'un fichier d'exemple"""
    print("\n🔍 Test d'import de fichier d'exemple...")
    
    config_file = "examples/ecommerce_config.yaml"
    if not os.path.exists(config_file):
        print(f"  ⚠️ Fichier {config_file} non trouvé")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = f.read()
        
        files = {'file': ('ecommerce_config.yaml', config_data, 'application/x-yaml')}
        response = requests.post('http://localhost:5000/api/configurations/import', files=files)
        
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        
        if response.status_code == 200:
            print("  ✅ Import de fichier réussi")
            return True
        else:
            print("  ❌ Import de fichier échoué")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def test_config_endpoints():
    """Teste les endpoints de configuration"""
    print("\n🔍 Test des endpoints de configuration...")
    
    base_url = "http://localhost:5000"
    
    # Test de liste des configurations
    try:
        response = requests.get(f"{base_url}/api/configurations")
        print(f"  Liste configs: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    Configurations: {len(data.get('configurations', []))}")
    except Exception as e:
        print(f"  ❌ Erreur liste: {e}")
    
    # Test d'export
    try:
        response = requests.post(f"{base_url}/api/configurations/export", json={
            'config_name': 'test_config'
        })
        print(f"  Export config: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Erreur export: {e}")

def main():
    """Fonction principale"""
    print("🧪 TEST D'IMPORT DE CONFIGURATION")
    print("=" * 50)
    
    # Vérifier que l'API est accessible
    try:
        response = requests.get("http://localhost:5000/api/health")
        if response.status_code != 200:
            print("❌ API non accessible")
            return False
        print("✅ API accessible")
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False
    
    # Tests d'import
    tests = [
        ("Configuration simple", test_simple_config),
        ("Configuration complète", test_complete_config),
        ("Fichier d'exemple", test_file_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Test des endpoints
    test_config_endpoints()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DES TESTS D'IMPORT")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS D'IMPORT RÉUSSIS !")
        return True
    else:
        print("⚠️ Certains tests d'import ont échoué")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 