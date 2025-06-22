#!/usr/bin/env python3
"""
Script de démarrage de l'API Admin
"""

import sys
import os

# Ajoute le répertoire parent (racine du projet) au path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Remonte d'un niveau
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if __name__ == "__main__":
    from src.api.admin_api import app
    from src.core.knowledge_base import KnowledgeBase
    from src.core.rule_engine import RuleEngine
    from src.rag.vector_store import VectorStore
    from src.config.config_manager import config_manager
    
    print("🚀 Démarrage de l'API Admin...")
    print("📍 Port: 5001")
    print("🌐 URL: http://localhost:5001")
    print("=" * 50)
    
    try:
        # Initialise les composants
        kb = KnowledgeBase()
        re = RuleEngine()
        vs = VectorStore()
        
        # Configure l'application Flask
        app.config['KNOWLEDGE_BASE'] = kb
        app.config['RULE_ENGINE'] = re
        app.config['VECTOR_STORE'] = vs
        app.config['CONFIG_MANAGER'] = config_manager
        
        # Démarre le serveur
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 API Admin arrêtée par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de l'API Admin: {e}") 