#!/usr/bin/env python3
"""
Script de debug/import pour le PoC
Permet de tester l'import de modules et la configuration du système
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config_manager import ConfigurationManager
from src.rule_engine import AdvancedRuleEngine
from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore

# Exemple d'utilisation/debug
if __name__ == "__main__":
    print("=== Debug Import System ===")
    kb = KnowledgeBase()
    vs = VectorStore()
    config_mgr = ConfigurationManager()
    rule_engine = AdvancedRuleEngine()
    print("✅ Import et initialisation réussis !")
    # Ajoute ici tes tests ou débogages spécifiques 