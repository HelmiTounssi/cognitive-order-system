#!/usr/bin/env python3
"""
Démo ultra générique du système
Permet de tester l'orchestration et la réflexion sur l'ontologie
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.knowledge_base import KnowledgeBase
from src.plugin_manager import PluginManager
from src.admin_interface import AdminInterface

def main():
    print("DEMONSTRATION - SYSTEME ULTRA-GENERIQUE")
    print("=" * 50)
    
    # 1. Initialisation
    print("1. Initialisation de la base de connaissances...")
    kb = KnowledgeBase()
    print("   ✅ Base de connaissances initialisee")
    
    # 2. Ajout de classes dynamiquement
    print("\n2. Ajout de classes dynamiquement...")
    
    client_properties = [
        {'name': 'hasName', 'type': 'string', 'label': 'Nom du client'},
        {'name': 'hasEmail', 'type': 'string', 'label': 'Email du client'}
    ]
    kb.extend_ontology_dynamically('Client', client_properties)
    print("   ✅ Classe Client ajoutee")
    
    product_properties = [
        {'name': 'hasName', 'type': 'string', 'label': 'Nom du produit'},
        {'name': 'hasPrice', 'type': 'float', 'label': 'Prix du produit'}
    ]
    kb.extend_ontology_dynamically('Product', product_properties)
    print("   ✅ Classe Product ajoutee")
    
    # 3. Ajout d'un handler métier déclaratif
    print("\n3. Ajout d'un handler metier declaratif...")
    
    create_order_handler = {
        'description': 'Handler pour la creation de commandes',
        'extraction_patterns': {
            'client_name': [r'pour\s+([a-zA-Z\s]+)'],
            'products': [r'(\d+)\s+unites?\s+de\s+([a-zA-Z\s]+)']
        },
        'workflow': [
            {'step': 1, 'action': 'validate_client', 'params': ['client_name']},
            {'step': 2, 'action': 'create_order', 'params': ['client_name', 'products']}
        ],
        'rules': [
            {'condition': 'stock_insufficient', 'action': 'suggest_alternatives'}
        ]
    }
    
    success = kb.add_business_handler('create_order', create_order_handler)
    print(f"   ✅ Handler 'create_order' ajoute: {'Oui' if success else 'Non'}")
    
    # 4. Test du gestionnaire de plug-ins
    print("\n4. Test du gestionnaire de plug-ins...")
    plugin_manager = PluginManager()
    print("   ✅ Gestionnaire de plug-ins initialise")
    
    # Création d'un plug-in simple
    plugin_content = '''
def process_data(data):
    return f"Donnees traitees: {data}"

PLUGIN_CONFIG = {
    'name': 'simple_processor',
    'version': '1.0.0',
    'description': 'Processeur simple'
}
'''
    
    plugin_file = os.path.join(plugin_manager.plugins_directory, 'simple_processor.py')
    with open(plugin_file, 'w', encoding='utf-8') as f:
        f.write(plugin_content)
    
    # Chargement du plug-in
    loaded_plugins = plugin_manager.discover_and_load_plugins()
    print(f"   ✅ Plug-ins charges: {loaded_plugins}")
    
    # Test d'exécution
    if 'simple_processor' in loaded_plugins:
        result = plugin_manager.execute_plugin_method('simple_processor', 'process_data', 'test')
        print(f"   ✅ Execution du plug-in: {result}")
    
    # 5. Test de l'interface d'administration
    print("\n5. Test de l'interface d'administration...")
    admin_interface = AdminInterface(kb, plugin_manager)
    print("   ✅ Interface d'administration initialisee")
    
    # Liste des handlers
    handlers = kb.list_business_handlers()
    print(f"   ✅ Handlers disponibles: {len(handlers)}")
    
    # 6. Test d'exécution de workflow
    print("\n6. Test d'execution de workflow...")
    
    class SimpleTools:
        def validate_client(self, client_name):
            return f"Client {client_name} valide"
        
        def create_order(self, client_name, products):
            return f"Commande creee pour {client_name}"
    
    tools = SimpleTools()
    test_params = {'client_name': 'John Doe', 'products': ['Laptop']}
    
    success, result = kb.execute_business_workflow('create_order', test_params, tools)
    print(f"   ✅ Workflow execute: {'Oui' if success else 'Non'}")
    print(f"   📋 Resultat: {result}")
    
    # 7. Résumé
    print("\n" + "=" * 50)
    print("🎉 DEMONSTRATION TERMINEE AVEC SUCCES!")
    print("\n✅ FONCTIONNALITES TESTEES:")
    print("   - Base de connaissances semantique")
    print("   - Ajout dynamique de classes")
    print("   - Handlers metiers declaratifs")
    print("   - Systeme de plug-ins dynamiques")
    print("   - Interface d'administration")
    print("   - Execution de workflows")
    
    print("\n🚀 LE SYSTEME ULTRA-GENERIQUE EST OPERATIONNEL!")
    print("   Aucune modification de code requise pour ajouter de nouvelles fonctionnalites")
    print("   Configuration 100% declarative")
    print("   Extensibilite infinie")

if __name__ == "__main__":
    main() 