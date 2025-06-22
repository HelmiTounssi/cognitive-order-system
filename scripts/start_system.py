#!/usr/bin/env python3
"""
Script principal de démarrage du système cognitif
Démarre l'API backend et l'interface d'administration
"""

import os
import sys
import subprocess
import time
import threading
import signal
import atexit

# Variables globales pour les processus
backend_process = None
frontend_process = None

def signal_handler(signum, frame):
    """Gestionnaire de signal pour arrêter proprement les processus"""
    print("\n🛑 Arrêt du système...")
    stop_processes()
    sys.exit(0)

def stop_processes():
    """Arrête tous les processus en cours"""
    global backend_process, frontend_process
    
    if backend_process:
        print("🛑 Arrêt du backend...")
        backend_process.terminate()
        backend_process.wait()
    
    if frontend_process:
        print("🛑 Arrêt du frontend...")
        frontend_process.terminate()
        frontend_process.wait()

def start_backend():
    """Démarre l'API backend"""
    global backend_process
    
    print("🚀 Démarrage de l'API Backend...")
    try:
        backend_process = subprocess.Popen([
            sys.executable, 'start_admin_api.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Attendre un peu pour que le serveur démarre
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Backend démarré sur http://localhost:5000")
            return True
        else:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Erreur backend: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du backend: {e}")
        return False

def start_frontend():
    """Démarre le frontend React"""
    global frontend_process
    
    print("🎨 Démarrage du Frontend...")
    try:
        frontend_process = subprocess.Popen([
            'npm', 'run', 'dev'
        ], cwd='admin-frontend', stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Attendre un peu pour que le serveur démarre
        time.sleep(5)
        
        if frontend_process.poll() is None:
            print("✅ Frontend démarré sur http://localhost:5173")
            return True
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"❌ Erreur frontend: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du frontend: {e}")
        return False

def check_dependencies():
    """Vérifie les dépendances nécessaires"""
    print("🔍 Vérification des dépendances...")
    
    # Vérifier Python et pip
    try:
        subprocess.run([sys.executable, '--version'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Python non trouvé")
        return False
    
    # Vérifier Node.js
    try:
        subprocess.run(['node', '--version'], check=True, capture_output=True)
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js ou npm non trouvé")
        print("💡 Installez Node.js depuis: https://nodejs.org/")
        return False
    
    print("✅ Toutes les dépendances sont installées")
    return True

def main():
    """Fonction principale"""
    print("🧠 SYSTÈME COGNITIF DE GESTION DE COMMANDE")
    print("=" * 50)
    
    # Configuration des signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(stop_processes)
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Vérifier que les dossiers existent
    if not os.path.exists('admin-frontend'):
        print("❌ Dossier admin-frontend non trouvé")
        sys.exit(1)
    
    # Installer les dépendances npm si nécessaire
    if not os.path.exists('admin-frontend/node_modules'):
        print("📦 Installation des dépendances npm...")
        try:
            subprocess.run(['npm', 'install'], cwd='admin-frontend', check=True)
            print("✅ Dépendances npm installées")
        except subprocess.CalledProcessError:
            print("❌ Erreur lors de l'installation des dépendances npm")
            sys.exit(1)
    
    # Démarrer le backend
    if not start_backend():
        print("❌ Impossible de démarrer le backend")
        sys.exit(1)
    
    # Démarrer le frontend
    if not start_frontend():
        print("❌ Impossible de démarrer le frontend")
        stop_processes()
        sys.exit(1)
    
    print("\n🎉 SYSTÈME DÉMARRÉ AVEC SUCCÈS !")
    print("=" * 50)
    print("🌐 Interface d'administration: http://localhost:5173")
    print("🔌 API Backend: http://localhost:5000")
    print("📋 Documentation: http://localhost:5000/api/health")
    print("\n⏹️  Appuyez sur Ctrl+C pour arrêter le système")
    
    # Maintenir le script en vie
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système...")
        stop_processes()

if __name__ == "__main__":
    main() 