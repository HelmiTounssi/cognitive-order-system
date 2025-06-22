#!/usr/bin/env python3
"""
Script de test simple pour diagnostiquer les problèmes de l'API
"""

import sys
import os

# Ajouter la racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

def test_imports():
    """Teste tous les imports nécessaires"""
    print("🔍 Test des imports...")
    
    try:
        print("  • Import de Flask...")
        from flask import Flask
        print("    ✅ Flask OK")
    except Exception as e:
        print(f"    ❌ Flask: {e}")
        return False
    
    try:
        print("  • Import de yaml...")
        import yaml
        print("    ✅ yaml OK")
    except Exception as e:
        print(f"    ❌ yaml: {e}")
        return False
    
    try:
        print("  • Import de rule_engine...")
        from src.core.rule_engine import AdvancedRuleEngine
        print("    ✅ rule_engine OK")
    except Exception as e:
        print(f"    ❌ rule_engine: {e}")
        return False
    
    try:
        print("  • Import de knowledge_base...")
        from src.knowledge_base import KnowledgeBase
        print("    ✅ knowledge_base OK")
    except Exception as e:
        print(f"    ❌ knowledge_base: {e}")
        return False
    
    try:
        print("  • Import de admin_api...")
        from src.api.admin_api import app
        print("    ✅ admin_api OK")
        return True
    except Exception as e:
        print(f"    ❌ admin_api: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app():
    """Teste la création de l'app Flask"""
    print("\n🔍 Test de l'app Flask...")
    
    try:
        from src.api.admin_api import app
        print("  ✅ App Flask créée avec succès")
        
        # Test d'un endpoint simple
        with app.test_client() as client:
            response = client.get('/api/health')
            print(f"  ✅ Endpoint /api/health: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"  ❌ Erreur Flask: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    print("🧪 DIAGNOSTIC DE L'API ADMIN")
    print("=" * 40)
    
    # Test des imports
    if not test_imports():
        print("\n❌ Échec des tests d'import")
        return False
    
    # Test de l'app Flask
    if not test_flask_app():
        print("\n❌ Échec des tests Flask")
        return False
    
    print("\n✅ TOUS LES TESTS RÉUSSIS !")
    print("🎉 L'API est prête à démarrer")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 