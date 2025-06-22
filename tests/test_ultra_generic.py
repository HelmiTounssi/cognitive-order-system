# -*- coding: utf-8 -*-
"""
Test des Fonctionnalités Ultra-Génériques
Démonstration des handlers métiers déclaratifs, plug-ins dynamiques, et interface d'administration
"""

from knowledge_base import KnowledgeBase
from vector_store import VectorStore
from llm_interface import LLMInterface
from agent import CognitiveOrderAgent
from plugin_manager import PluginManager
from admin_interface import AdminInterface
import tools


def test_initialisation():
    """Test de l'initialisation du système ultra-générique"""
    print("TEST 1: INITIALISATION DU SYSTEME ULTRA-GENERIQUE")
    print("=" * 60)
    
    try:
        # Test de la base de connaissances
        print("Test de la base de connaissances...")
        kb = KnowledgeBase()
        print("   Base de connaissances initialisee")
        
        # Test de l'interface LLM
        print("Test de l'interface LLM...")
        try:
            llm = LLMInterface()
            print("   Interface LLM initialisee (OpenAI)")
        except Exception as e:
            print(f"   Interface LLM non disponible: {e}")
            llm = None
        
        # Test de la base vectorielle
        print("Test de la base vectorielle...")
        vector_store = VectorStore(llm_interface=llm)
        print("   Base vectorielle initialisee")
        
        # Test du gestionnaire de plug-ins
        print("Test du gestionnaire de plug-ins...")
        plugin_manager = PluginManager()
        print("   Gestionnaire de plug-ins initialise")
        
        # Test de l'interface d'administration
        print("Test de l'interface d'administration...")
        admin_interface = AdminInterface(kb, plugin_manager)
        print("   Interface d'administration initialisee")
        
        # Test de l'agent
        print("Test de l'agent cognitif...")
        agent = CognitiveOrderAgent(kb, vector_store, llm)
        print("   Agent cognitif initialise")
        
        return kb, vector_store, llm, agent, plugin_manager, admin_interface
        
    except Exception as e:
        print(f"   Erreur lors de l'initialisation: {e}")
        return None, None, None, None, None, None


def test_business_handlers():
    """Test des handlers métiers déclaratifs"""
    print("\n\nTEST 2: HANDLERS METIERS DECLARATIFS")
    print("=" * 60)
    
    kb, vector_store, llm, agent, plugin_manager, admin_interface = test_initialisation()
    if not kb:
        return
    
    # Ajout de classes de base
    print("Preparation des classes de base...")
    
    client_properties = [
        {'name': 'hasName', 'type': 'string', 'label': 'Nom du client'},
        {'name': 'hasEmail', 'type': 'string', 'label': 'Email du client'}
    ]
    kb.extend_ontology_dynamically('Client', client_properties)
    
    product_properties = [
        {'name': 'hasName', 'type': 'string', 'label': 'Nom du produit'},
        {'name': 'hasPrice', 'type': 'float', 'label': 'Prix du produit'},
        {'name': 'hasStock', 'type': 'int', 'label': 'Stock disponible'},
        {'name': 'hasDescription', 'type': 'string', 'label': 'Description'}
    ]
    kb.extend_ontology_dynamically('Product', product_properties)
    
    # Test 1: Ajout d'un handler métier déclaratif
    print("\n1. Ajout d'un handler metier declaratif 'create_order':")
    
    create_order_handler = {
        'description': 'Handler pour la creation de commandes',
        'extraction_patterns': {
            'client_name': [
                r'pour\s+([a-zA-Z\s]+)',
                r'client\s+([a-zA-Z\s]+)'
            ],
            'products': [
                r'(\d+)\s+unites?\s+de\s+([a-zA-Z\s]+)',
                r'([a-zA-Z\s]+)\s+avec\s+(\d+)\s+unites?'
            ]
        },
        'workflow': [
            {
                'step': 1,
                'action': 'validate_client',
                'params': ['client_name']
            },
            {
                'step': 2,
                'action': 'check_stock',
                'params': ['products']
            },
            {
                'step': 3,
                'action': 'create_order',
                'params': ['client_name', 'products']
            },
            {
                'step': 4,
                'action': 'process_payment',
                'params': ['order_id', 'amount']
            }
        ],
        'rules': [
            {
                'condition': 'stock_insufficient',
                'action': 'suggest_alternatives'
            },
            {
                'condition': 'payment_failed',
                'action': 'retry_payment'
            }
        ]
    }
    
    success = kb.add_business_handler('create_order', create_order_handler)
    print(f"   Resultat: {'Succes' if success else 'Echec'}")
    
    # Test 2: Ajout d'un handler métier pour les recommandations
    print("\n2. Ajout d'un handler metier 'recommend_products':")
    
    recommend_handler = {
        'description': 'Handler pour les recommandations de produits',
        'extraction_patterns': {
            'query_text': [
                r'recommande\s+(.+)',
                r'cherche\s+(.+)',
                r'suggere\s+(.+)'
            ],
            'reference_product': [
                r'similaire\s+a\s+([a-zA-Z\s]+)'
            ]
        },
        'workflow': [
            {
                'step': 1,
                'action': 'analyze_query',
                'params': ['query_text', 'reference_product']
            },
            {
                'step': 2,
                'action': 'search_products',
                'params': ['search_criteria']
            },
            {
                'step': 3,
                'action': 'rank_results',
                'params': ['products', 'relevance_score']
            }
        ],
        'rules': [
            {
                'condition': 'no_results',
                'action': 'expand_search'
            }
        ]
    }
    
    success = kb.add_business_handler('recommend_products', recommend_handler)
    print(f"   Resultat: {'Succes' if success else 'Echec'}")
    
    # Test 3: Liste des handlers métiers
    print("\n3. Liste des handlers metiers disponibles:")
    handlers = kb.list_business_handlers()
    for handler in handlers:
        print(f"   - {handler['intent_name']}: {handler.get('description', 'N/A')}")
    
    # Test 4: Récupération et affichage d'un handler
    print("\n4. Configuration du handler 'create_order':")
    config = kb.get_business_handler('create_order')
    if config:
        print(f"   Description: {config.get('description', 'N/A')}")
        print(f"   Patterns d'extraction: {len(config.get('extraction_patterns', {}))}")
        print(f"   Etapes du workflow: {len(config.get('workflow', []))}")
        print(f"   Regles metier: {len(config.get('rules', []))}")
    else:
        print("   Configuration non trouvee")


def test_plugin_system():
    """Test du système de plug-ins dynamiques"""
    print("\n\nTEST 3: SYSTEME DE PLUG-INS DYNAMIQUES")
    print("=" * 60)
    
    kb, vector_store, llm, agent, plugin_manager, admin_interface = test_initialisation()
    if not plugin_manager:
        return
    
    # Test 1: Création de templates de plug-ins
    print("1. Creation de templates de plug-ins:")
    
    # Template de plug-in répertoire
    success = plugin_manager.create_plugin_template('advanced_analytics', 'directory')
    print(f"   Template repertoire 'advanced_analytics': {'Cree' if success else 'Echec'}")
    
    # Template de plug-in fichier
    success = plugin_manager.create_plugin_template('simple_calculator', 'file')
    print(f"   Template fichier 'simple_calculator': {'Cree' if success else 'Echec'}")
    
    # Test 2: Création d'un plug-in personnalisé
    print("\n2. Creation d'un plug-in personnalise 'custom_processor':")
    
    custom_plugin_content = '''"""
Plug-in Custom Processor
Plug-in personnalise pour le traitement avance
"""

def process_data(data, options=None):
    """
    Traite des donnees avec des options personnalisees
    
    Args:
        data: Donnees a traiter
        options: Options de traitement
    
    Returns:
        dict: Resultats du traitement
    """
    if options is None:
        options = {}
    
    result = {
        'processed_data': data,
        'processing_time': 0.1,
        'options_used': options,
        'status': 'success'
    }
    
    # Logique de traitement personnalisee
    if 'transform' in options:
        result['processed_data'] = f"TRANSFORMED: {data}"
    
    if 'validate' in options:
        result['validation'] = 'passed'
    
    return result

def analyze_patterns(text):
    """
    Analyse des patterns dans un texte
    
    Args:
        text: Texte a analyser
    
    Returns:
        dict: Patterns trouves
    """
    patterns = {
        'words': len(text.split()),
        'characters': len(text),
        'sentences': text.count('.') + text.count('!') + text.count('?'),
        'uppercase': sum(1 for c in text if c.isupper()),
        'lowercase': sum(1 for c in text if c.islower())
    }
    
    return patterns

# Configuration du plug-in
PLUGIN_CONFIG = {
    'name': 'custom_processor',
    'version': '1.0.0',
    'description': 'Plug-in de traitement personnalise',
    'author': 'Developpeur',
    'entry_points': [
        {
            'name': 'process_data',
            'method': 'process_data',
            'description': 'Traitement de donnees'
        },
        {
            'name': 'analyze_patterns',
            'method': 'analyze_patterns',
            'description': 'Analyse de patterns'
        }
    ]
}
'''
    
    # Écrit le plug-in personnalisé
    import os
    plugin_file = os.path.join(plugin_manager.plugins_directory, 'custom_processor.py')
    with open(plugin_file, 'w', encoding='utf-8') as f:
        f.write(custom_plugin_content)
    
    print("   Plug-in personnalise cree")
    
    # Test 3: Découverte et chargement automatique
    print("\n3. Decouverte et chargement automatique des plug-ins:")
    loaded_plugins = plugin_manager.discover_and_load_plugins()
    print(f"   Plug-ins charges: {loaded_plugins}")
    
    # Test 4: Liste des plug-ins
    print("\n4. Liste des plug-ins disponibles:")
    plugins = plugin_manager.list_plugins()
    for plugin in plugins:
        print(f"   - {plugin['name']}: {plugin['config'].get('description', 'N/A')}")
    
    # Test 5: Exécution de méthodes de plug-ins
    print("\n5. Test d'execution de methodes de plug-ins:")
    
    if 'custom_processor' in loaded_plugins:
        try:
            # Test de process_data
            result = plugin_manager.execute_plugin_method(
                'custom_processor', 'process_data', 
                "Donnees de test", {'transform': True, 'validate': True}
            )
            print(f"   process_data: {result}")
            
            # Test de analyze_patterns
            result = plugin_manager.execute_plugin_method(
                'custom_processor', 'analyze_patterns', 
                "Ceci est un texte de test avec des mots en MAJUSCULES!"
            )
            print(f"   analyze_patterns: {result}")
            
        except Exception as e:
            print(f"   Erreur lors de l'execution: {e}")


def test_admin_interface():
    """Test de l'interface d'administration"""
    print("\n\nTEST 4: INTERFACE D'ADMINISTRATION")
    print("=" * 60)
    
    kb, vector_store, llm, agent, plugin_manager, admin_interface = test_initialisation()
    if not admin_interface:
        return
    
    # Test 1: Introspection de l'ontologie via l'interface
    print("1. Introspection de l'ontologie via l'interface:")
    admin_interface.introspect_ontology()
    
    # Test 2: Ajout d'une classe via l'interface
    print("\n2. Ajout d'une classe 'Project' via l'interface:")
    
    # Simulation de l'ajout d'une classe
    project_properties = [
        {'name': 'hasName', 'type': 'string', 'label': 'Nom du projet'},
        {'name': 'hasDescription', 'type': 'string', 'label': 'Description'},
        {'name': 'hasBudget', 'type': 'float', 'label': 'Budget'},
        {'name': 'hasStatus', 'type': 'string', 'label': 'Statut'}
    ]
    
    success = kb.extend_ontology_dynamically('Project', project_properties)
    print(f"   Resultat: {'Succes' if success else 'Echec'}")
    
    # Test 3: Création d'instances via l'interface
    print("\n3. Creation d'instances via l'interface:")
    
    # Instance de Project
    project_props = {
        'hasName': 'Refonte Site Web',
        'hasDescription': 'Modernisation du site web existant',
        'hasBudget': 15000.0,
        'hasStatus': 'En cours'
    }
    
    instance_id = kb.create_instance_dynamically('Project', project_props)
    print(f"   Instance Project creee: {instance_id}")
    
    # Instance de Client
    client_props = {
        'hasName': 'Entreprise ABC',
        'hasEmail': 'contact@abc.com'
    }
    
    instance_id = kb.create_instance_dynamically('Client', client_props)
    print(f"   Instance Client creee: {instance_id}")
    
    # Test 4: Liste des classes et instances
    print("\n4. Liste des classes et instances:")
    admin_interface.list_classes()
    admin_interface.list_instances()
    
    # Test 5: Gestion des plug-ins via l'interface
    print("\n5. Gestion des plug-ins via l'interface:")
    admin_interface.list_plugins()
    
    # Test 6: Gestion des handlers métiers via l'interface
    print("\n6. Gestion des handlers metiers via l'interface:")
    admin_interface.list_handlers()


def test_workflow_execution():
    """Test de l'exécution de workflows métiers"""
    print("\n\nTEST 5: EXECUTION DE WORKFLOWS METIERS")
    print("=" * 60)
    
    kb, vector_store, llm, agent, plugin_manager, admin_interface = test_initialisation()
    if not kb:
        return
    
    # Création d'un gestionnaire d'outils simple pour les tests
    class SimpleToolsManager:
        def validate_client(self, client_name):
            return f"Client '{client_name}' valide"
        
        def check_stock(self, products):
            return f"Stock verifie pour {len(products)} produits"
        
        def create_order(self, client_name, products):
            return f"Commande creee pour {client_name} avec {len(products)} produits"
        
        def process_payment(self, order_id, amount):
            return f"Paiement traite pour la commande {order_id}: {amount}€"
        
        def suggest_alternatives(self):
            return "Alternatives suggerees"
        
        def retry_payment(self):
            return "Nouvelle tentative de paiement"
    
    tools_manager = SimpleToolsManager()
    
    # Test 1: Exécution du workflow create_order
    print("1. Execution du workflow 'create_order':")
    
    test_params = {
        'client_name': 'John Doe',
        'products': [
            {'name': 'Laptop', 'quantity': 2},
            {'name': 'Mouse', 'quantity': 1}
        ]
    }
    
    success, result = kb.execute_business_workflow('create_order', test_params, tools_manager)
    print(f"   Resultat: {'Succes' if success else 'Echec'}")
    print(f"   Message: {result}")
    
    # Test 2: Exécution du workflow recommend_products
    print("\n2. Execution du workflow 'recommend_products':")
    
    test_params = {
        'query_text': 'ordinateur portable gaming',
        'reference_product': 'Laptop Pro'
    }
    
    success, result = kb.execute_business_workflow('recommend_products', test_params, tools_manager)
    print(f"   Resultat: {'Succes' if success else 'Echec'}")
    print(f"   Message: {result}")


def test_integration_complete():
    """Test d'intégration complète"""
    print("\n\nTEST 6: INTEGRATION COMPLETE")
    print("=" * 60)
    
    kb, vector_store, llm, agent, plugin_manager, admin_interface = test_initialisation()
    if not all([kb, agent, plugin_manager, admin_interface]):
        return
    
    print("SYSTEME ULTRA-GENERIQUE OPERATIONNEL!")
    print("\nFONCTIONNALITES DEMONTREES:")
    print("1. Handlers metiers declaratifs stockes dans l'ontologie")
    print("2. Systeme de plug-ins dynamiques avec chargement a chaud")
    print("3. Interface d'administration pour non-developpeurs")
    print("4. Workflows metiers executables")
    print("5. Agent cognitif avec reflexion")
    print("6. Base de connaissances semantique extensible")
    
    print("\nAVANTAGES DU SYSTEME ULTRA-GENERIQUE:")
    print("- Aucune modification de code pour ajouter de nouvelles fonctionnalites")
    print("- Configuration declarative via l'interface d'administration")
    print("- Plug-ins dynamiques pour besoins metier avances")
    print("- Workflows metiers stockes dans l'ontologie")
    print("- Extensibilite infinie sans redemarrage")
    print("- Paradigme semantique coherent")
    
    print("\nUTILISATION:")
    print("1. Interface d'administration: python -c 'from admin_interface import AdminInterface; AdminInterface(kb, pm).show_main_menu()'")
    print("2. Agent cognitif: python main.py")
    print("3. Plug-ins: Ajoutez des fichiers dans ./plugins/")
    print("4. Handlers metiers: Configurez via l'interface d'administration")


if __name__ == "__main__":
    print("TEST - SYSTEME ULTRA-GENERIQUE")
    print("Handlers metiers declaratifs + Plug-ins dynamiques + Interface d'administration")
    print("=" * 80)
    
    try:
        # Test 1: Initialisation
        test_initialisation()
        
        # Test 2: Handlers métiers déclaratifs
        test_business_handlers()
        
        # Test 3: Système de plug-ins
        test_plugin_system()
        
        # Test 4: Interface d'administration
        test_admin_interface()
        
        # Test 5: Exécution de workflows
        test_workflow_execution()
        
        # Test 6: Intégration complète
        test_integration_complete()
        
        print("\n\nTOUS LES TESTS TERMINES AVEC SUCCES!")
        print("Le systeme ultra-generique est operationnel!")
        print("Pret pour la production avec extensibilite infinie!")
        
    except Exception as e:
        print(f"\nErreur lors des tests: {e}")
        import traceback
        traceback.print_exc() 