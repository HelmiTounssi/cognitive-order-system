#!/usr/bin/env python3
"""
Script de test pour l'API de sauvegarde des workflows
"""

import requests
import json
from datetime import datetime

def test_api_save_workflow():
    """Test de l'API de sauvegarde de workflow"""
    print("🧪 Test de l'API de sauvegarde de workflow...")
    
    try:
        # Données de test
        workflow_data = {
            "workflow": [
                {
                    "step": 1,
                    "action": "Vérifier les antécédents",
                    "description": "Test description"
                }
            ],
            "metadata": {
                "name": f"test_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "domain": "test",
                "description": "Test workflow via API"
            }
        }
        
        # Appel à l'API
        response = requests.post(
            "http://localhost:5001/api/llm/save_workflow",
            json=workflow_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ API de sauvegarde fonctionne correctement")
            return True
        else:
            print("❌ Erreur dans l'API de sauvegarde")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test API: {e}")
        return False

def test_api_get_saved_items():
    """Test de l'API de récupération des éléments sauvegardés"""
    print("\n📝 Test de l'API de récupération des éléments sauvegardés...")
    
    try:
        response = requests.get("http://localhost:5001/api/llm/saved_items")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ API de récupération fonctionne correctement")
            return True
        else:
            print("❌ Erreur dans l'API de récupération")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test API: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Test de l'API de sauvegarde")
    print("=" * 60)
    
    # Test de sauvegarde
    save_success = test_api_save_workflow()
    
    # Test de récupération
    get_success = test_api_get_saved_items()
    
    print("\n" + "=" * 60)
    if save_success and get_success:
        print("✅ Tous les tests API réussis")
    else:
        print("❌ Certains tests API ont échoué")
    print("=" * 60) 