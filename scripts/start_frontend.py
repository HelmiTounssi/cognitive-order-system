#!/usr/bin/env python3
"""
Script de démarrage du frontend React
"""

import sys
import os
import subprocess
import webbrowser
import time

# Ajoute le répertoire parent (racine du projet) au path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Remonte d'un niveau
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_node_modules():
    """Vérifie si node_modules existe"""
    frontend_dir = os.path.join(project_root, "admin-frontend")
    node_modules = os.path.join(frontend_dir, "node_modules")
    return os.path.exists(node_modules)

def install_dependencies():
    """Installe les dépendances npm"""
    frontend_dir = os.path.join(project_root, "admin-frontend")
    print("📦 Installation des dépendances npm...")
    try:
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        print("✅ Dépendances installées")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erreur lors de l'installation des dépendances")
        return False

def start_dev_server():
    """Démarre le serveur de développement"""
    frontend_dir = os.path.join(project_root, "admin-frontend")
    print("🚀 Démarrage du serveur de développement...")
    print("📍 URL: http://localhost:3000")
    print("=" * 50)
    
    try:
        # Ouvre le navigateur après un délai
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:3000")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Démarre le serveur de développement
        subprocess.run(["npm", "start"], cwd=frontend_dir)
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur frontend arrêté par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du frontend: {e}")

if __name__ == "__main__":
    print("🎨 Démarrage du frontend React...")
    
    # Vérifie et installe les dépendances si nécessaire
    if not check_node_modules():
        if not install_dependencies():
            sys.exit(1)
    
    # Démarre le serveur de développement
    start_dev_server() 