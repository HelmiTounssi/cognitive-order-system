#!/usr/bin/env python3
"""
Script de démarrage pour l'API Admin Flask
Gère les imports et démarre le serveur d'administration
"""

import sys
import os
import subprocess

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    required_packages = ['flask', 'flask-cors', 'PyYAML', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PyYAML':
                import yaml
            elif package == 'flask-cors':
                import flask_cors
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Dépendances manquantes: {', '.join(missing_packages)}")
        print("💡 Installation des dépendances...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dépendances installées avec succès")
        except subprocess.CalledProcessError:
            print("❌ Erreur lors de l'installation des dépendances")
            return False
    
    return True

def main():
    """Fonction principale"""
    print("🚀 Démarrage de l'API Admin Flask...")
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Ajouter la racine du projet au PYTHONPATH
    sys.path.insert(0, os.path.abspath('.'))
    
    try:
        from src.api.admin_api import app
        
        print("📍 URL: http://localhost:5000")
        print("📋 Endpoints disponibles:")
        print("   • /api/rules - Gestion des règles métier")
        print("   • /api/configurations - Gestion des configurations")
        print("   • /api/ontology - Gestion de l'ontologie")
        print("   • /api/llm - Assistants LLM")
        print("   • /api/rag - Interface RAG")
        print("   • /api/system/status - Statut du système")
        print("   • /api/health - Vérification de santé")
        print("\n🔌 API prête à recevoir des requêtes...")
        print("⏹️  Appuyez sur Ctrl+C pour arrêter le serveur")
        
        # Démarrer le serveur Flask
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Éviter les problèmes de double import
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("💡 Assurez-vous que l'environnement virtuel est activé:")
        print("   poc_env\\Scripts\\activate")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 