#!/usr/bin/env python3
"""
Script d'exemple d'import YAML
Permet de tester l'import de configuration YAML dans le système
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigurationManager
from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore

if __name__ == "__main__":
    print("=== Import YAML Example ===")
    config_mgr = ConfigurationManager()
    kb = KnowledgeBase()
    vs = VectorStore()
    # Ajoute ici ton code d'import YAML ou de test
