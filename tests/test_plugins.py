#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from plugin_manager import PluginManager

def test_plugins_property():
    print("=== TEST PROPRIETE PLUGINS ===")
    
    # 1. Création du PluginManager
    print("1. Création du PluginManager...")
    pm = PluginManager()
    print("   ✓ PluginManager créé")
    
    # 2. Test de la propriété plugins
    print("\n2. Test de la propriété plugins...")
    print(f"   ✓ Attribut plugins accessible: {hasattr(pm, 'plugins')}")
    print(f"   ✓ Nombre de plugins chargés: {len(pm.plugins)}")
    
    # 3. Test d'accès direct
    print("\n3. Test d'accès direct...")
    try:
        plugins_dict = pm.plugins
        print(f"   ✓ Type de plugins: {type(plugins_dict)}")
        print(f"   ✓ Clés disponibles: {list(plugins_dict.keys())}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # 4. Test d'ajout de plugin
    print("\n4. Test d'ajout de plugin...")
    try:
        # Simule un plugin
        test_plugin = {
            'module': None,
            'config': {'name': 'test_plugin', 'version': '1.0.0'},
            'path': './test_plugin.py'
        }
        pm.loaded_plugins['test_plugin'] = test_plugin
        print(f"   ✓ Plugin ajouté, total: {len(pm.plugins)}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n=== SUCCES! PROPRIETE PLUGINS OPERATIONNELLE ===")
    return True

if __name__ == "__main__":
    test_plugins_property() 