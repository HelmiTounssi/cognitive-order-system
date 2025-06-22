#!/usr/bin/env python3
"""
Test complet du système cognitif
Valide tous les composants et fonctionnalités
"""

import sys
import os
import requests
import time
import json

# Ajouter la racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

def test_backend_api():
    """Teste l'API backend"""
    print("🔌 Test de l'API Backend...")
    
    base_url = "http://localhost:5000"
    
    # Test de santé
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("  ✅ Endpoint /api/health")
        else:
            print(f"  ❌ /api/health: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur /api/health: {e}")
        return False
    
    # Test des règles
    try:
        response = requests.get(f"{base_url}/api/rules")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Endpoint /api/rules ({data['total']} règles)")
        else:
            print(f"  ❌ /api/rules: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur /api/rules: {e}")
        return False
    
    # Test du statut système
    try:
        response = requests.get(f"{base_url}/api/system/status")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Endpoint /api/system/status (Statut: {data['system_status']['global_status']})")
        else:
            print(f"  ❌ /api/system/status: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur /api/system/status: {e}")
        return False
    
    return True

def test_frontend():
    """Teste le frontend React"""
    print("\n🎨 Test du Frontend...")
    
    try:
        response = requests.get("http://localhost:5173")
        if response.status_code == 200:
            print("  ✅ Frontend React accessible")
            return True
        else:
            print(f"  ❌ Frontend: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur frontend: {e}")
        return False

def test_plugin_system():
    """Teste le système de plugins"""
    print("\n🔌 Test du système de plugins...")
    
    try:
        from scripts.test_plugin_example import main as test_plugins
        test_plugins()
        print("  ✅ Système de plugins fonctionnel")
        return True
    except Exception as e:
        print(f"  ❌ Erreur plugins: {e}")
        return False

def test_config_import():
    """Teste l'import de configurations"""
    print("\n📋 Test d'import de configurations...")
    
    try:
        # Test avec un fichier d'exemple
        config_file = "examples/ecommerce_config.yaml"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = f.read()
            
            files = {'file': ('ecommerce_config.yaml', config_data, 'application/x-yaml')}
            response = requests.post("http://localhost:5000/api/configurations/import", files=files)
            
            if response.status_code == 200:
                print("  ✅ Import de configuration réussi")
                return True
            else:
                print(f"  ❌ Import config: {response.status_code}")
                return False
        else:
            print("  ⚠️ Fichier d'exemple non trouvé")
            return True
    except Exception as e:
        print(f"  ❌ Erreur import config: {e}")
        return False

def test_llm_assistants():
    """Teste les assistants LLM"""
    print("\n🤖 Test des assistants LLM...")
    
    try:
        # Test de génération de workflow
        test_data = {
            "domain": "ecommerce",
            "business_process": "gestion des commandes",
            "requirements": ["validation stock", "calcul prix", "gestion livraison"]
        }
        
        response = requests.post("http://localhost:5000/api/llm/generate_workflow", json=test_data)
        if response.status_code == 200:
            print("  ✅ Génération de workflow LLM")
            return True
        else:
            print(f"  ❌ LLM workflow: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur LLM: {e}")
        return False

def test_rag_system():
    """Teste le système RAG"""
    print("\n🔍 Test du système RAG...")
    
    try:
        # Test de création de conversation
        response = requests.post("http://localhost:5000/api/rag/conversations", json={
            "title": "Test conversation",
            "description": "Test du système RAG"
        })
        
        if response.status_code == 200:
            print("  ✅ Création de conversation RAG")
            return True
        else:
            print(f"  ❌ RAG conversation: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erreur RAG: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST COMPLET DU SYSTÈME COGNITIF")
    print("=" * 50)
    
    tests = [
        ("API Backend", test_backend_api),
        ("Frontend React", test_frontend),
        ("Système de plugins", test_plugin_system),
        ("Import de configurations", test_config_import),
        ("Assistants LLM", test_llm_assistants),
        ("Système RAG", test_rag_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des résultats
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DES TESTS")
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
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("🚀 Le système cognitif est entièrement opérationnel")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 