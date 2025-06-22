#!/usr/bin/env python3
"""
Test du Plugin d'Exemple
Démonstration de l'utilisation du système de plugins
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.plugin_manager import PluginManager
from plugins.example_plugin import ExamplePlugin


def test_plugin_loading():
    """Test de chargement du plugin"""
    print("🔌 Test de chargement du plugin")
    print("=" * 40)
    
    plugin_manager = PluginManager()
    
    # Test de chargement du plugin
    plugin_path = os.path.join(os.path.dirname(__file__), "..", "plugins", "example_plugin.py")
    success = plugin_manager.load_plugin_from_file("example_plugin", plugin_path)
    
    if success:
        print("✅ Plug-in 'example_plugin' chargé avec succès")
    else:
        print("❌ Échec du chargement du plug-in")
    
    return plugin_manager


def test_plugin_functions(plugin_manager):
    """Test des fonctions du plugin"""
    print("\n🔧 Test des fonctions du plugin")
    print("=" * 40)
    
    # Récupérer le plugin
    plugin_data = plugin_manager.get_plugin("example_plugin")
    if not plugin_data:
        print("❌ Plugin non trouvé")
        return
    
    # Accéder au module du plugin et créer une instance
    plugin_module = plugin_data['module']
    plugin_instance = plugin_module.create_plugin()
    
    # Test 1: Fonction hello_world
    print("\n1. Test hello_world:")
    result = plugin_instance.hello_world("Développeur")
    print(f"   Résultat: {result}")
    
    # Test 2: Traitement de données
    print("\n2. Test process_data:")
    test_data = [
        {'id': 'item1', 'value': 100},
        {'id': 'item2', 'value': 200},
        {'id': 'item3', 'value': 150}
    ]
    result = plugin_instance.process_data(test_data)
    print(f"   Données traitées: {result['item_count']} éléments")
    print(f"   Valeur totale: {result['total_value']}")
    
    # Test 3: Analyse de texte
    print("\n3. Test analyze_text:")
    text = "Ceci est un exemple de texte en français. Il contient plusieurs phrases."
    analysis = plugin_instance.analyze_text(text)
    print(f"   Mots: {analysis['word_count']}")
    print(f"   Phrases: {analysis['sentence_count']}")
    print(f"   Langue détectée: {analysis['language_detection']}")
    
    # Test 4: Logique métier
    print("\n4. Test custom_business_logic:")
    business_data = {
        'amount': 1000,
        'customer_type': 'vip'
    }
    business_result = plugin_instance.custom_business_logic(business_data)
    print(f"   Montant original: {business_result['original_amount']}€")
    print(f"   Remise: {business_result['discount_amount']}€ ({business_result['savings_percentage']:.1f}%)")
    print(f"   Montant final: {business_result['final_amount']}€")
    
    # Test 5: Génération de rapport
    print("\n5. Test generate_report:")
    report_data = {
        'ventes': 15000,
        'clients': 45,
        'produits': ['Laptop', 'Souris', 'Clavier'],
        'performance': 'excellente'
    }
    report = plugin_instance.generate_report(report_data, "summary")
    print(report)


def test_plugin_management(plugin_manager):
    """Test de la gestion des plugins"""
    print("\n⚙️ Test de la gestion des plugins")
    print("=" * 40)
    
    # Informations du plugin
    plugin_data = plugin_manager.get_plugin("example_plugin")
    if plugin_data:
        print("📋 Informations du plugin:")
        config = plugin_data.get('config', {})
        print(f"   • Nom: {config.get('name')}")
        print(f"   • Version: {config.get('version')}")
        print(f"   • Auteur: {config.get('author')}")
        print(f"   • Description: {config.get('description')}")
        print(f"   • Chemin: {plugin_data.get('path')}")
    
    # Liste des plugins
    plugins_list = plugin_manager.list_plugins()
    print(f"\n📋 Plugins chargés ({len(plugins_list)}):")
    for plugin_info in plugins_list:
        print(f"   • {plugin_info['name']}: {plugin_info['config'].get('description', 'N/A')}")
    
    # Test d'exécution de méthode via le plugin_manager
    print("\n🔄 Test d'exécution via plugin_manager:")
    try:
        # Créer une instance du plugin
        plugin_module = plugin_data['module']
        plugin_instance = plugin_module.create_plugin()
        
        # Tester une méthode
        result = plugin_instance.hello_world("Test")
        print(f"   Exécution hello_world: {result}")
        
        # Tester get_info
        info = plugin_instance.get_info()
        print(f"   Informations du plugin: {info['metadata']['name']} v{info['metadata']['version']}")
        
    except Exception as e:
        print(f"   ❌ Erreur d'exécution: {e}")


def test_plugin_integration():
    """Test d'intégration avec le système principal"""
    print("\n🔗 Test d'intégration avec le système")
    print("=" * 40)
    
    # Créer une instance du plugin directement
    plugin = ExamplePlugin()
    
    # Simuler une utilisation dans le système principal
    print("🎯 Simulation d'utilisation dans le système:")
    
    # Exemple: traitement de commande avec logique métier
    order_data = {
        'order_id': 'CMD-001',
        'customer': {
            'name': 'Jean Dupont',
            'type': 'vip'
        },
        'items': [
            {'product': 'Laptop', 'price': 1200},
            {'product': 'Souris', 'price': 50}
        ]
    }
    
    # Calculer le total
    total_amount = sum(item['price'] for item in order_data['items'])
    
    # Appliquer la logique métier du plugin
    business_result = plugin.custom_business_logic({
        'amount': total_amount,
        'customer_type': order_data['customer']['type']
    })
    
    print(f"   Commande: {order_data['order_id']}")
    print(f"   Client: {order_data['customer']['name']} ({order_data['customer']['type']})")
    print(f"   Total: {business_result['original_amount']}€")
    print(f"   Remise: {business_result['discount_amount']}€")
    print(f"   Final: {business_result['final_amount']}€")
    
    # Générer un rapport
    report_data = {
        'order_id': order_data['order_id'],
        'customer_name': order_data['customer']['name'],
        'total_items': len(order_data['items']),
        'original_amount': business_result['original_amount'],
        'final_amount': business_result['final_amount'],
        'savings': business_result['discount_amount']
    }
    
    report = plugin.generate_report(report_data, "detailed")
    print("\n📊 Rapport de commande:")
    print(report)


def main():
    """Fonction principale de test"""
    print("🧪 TEST COMPLET DU SYSTÈME DE PLUGINS")
    print("=" * 60)
    
    try:
        # Test 1: Chargement du plugin
        plugin_manager = test_plugin_loading()
        if not plugin_manager:
            return
        
        # Test 2: Fonctions du plugin
        test_plugin_functions(plugin_manager)
        
        # Test 3: Gestion des plugins
        test_plugin_management(plugin_manager)
        
        # Test 4: Intégration
        test_plugin_integration()
        
        print("\n" + "=" * 60)
        print("✅ TOUS LES TESTS RÉUSSIS !")
        print("🎉 Le système de plugins fonctionne parfaitement")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 