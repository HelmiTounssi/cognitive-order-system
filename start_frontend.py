#!/usr/bin/env python3
"""
Script de démarrage pour le Frontend React
Démarre l'interface d'administration en mode développement
"""

import os
import sys
import subprocess
import time

def check_node_installed():
    """Vérifie si Node.js est installé"""
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_dependencies():
    """Installe les dépendances npm"""
    print("📦 Installation des dépendances npm...")
    try:
        subprocess.run(['npm', 'install'], cwd='admin-frontend', check=True)
        print("✅ Dépendances npm installées")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def start_frontend():
    """Démarre le serveur de développement React"""
    print("🚀 Démarrage du Frontend React...")
    print("📍 URL: http://localhost:5173")
    print("🔌 Interface d'administration prête...")
    print("⏹️  Appuyez sur Ctrl+C pour arrêter le serveur")
    
    try:
        subprocess.run(['npm', 'run', 'dev'], cwd='admin-frontend', check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Serveur frontend arrêté")
        return True

def main():
    """Fonction principale"""
    print("🎨 Démarrage de l'Interface d'Administration")
    print("=" * 50)
    
    # Vérifier Node.js
    if not check_node_installed():
        print("❌ Node.js et npm ne sont pas installés")
        print("💡 Installez Node.js depuis: https://nodejs.org/")
        sys.exit(1)
    
    # Vérifier que le dossier admin-frontend existe
    if not os.path.exists('admin-frontend'):
        print("❌ Dossier admin-frontend non trouvé")
        print("💡 Assurez-vous d'être dans le répertoire racine du projet")
        sys.exit(1)
    
    # Installer les dépendances si nécessaire
    if not os.path.exists('admin-frontend/node_modules'):
        if not install_dependencies():
            sys.exit(1)
    
    # Démarrer le frontend
    start_frontend()

if __name__ == "__main__":
    main() 