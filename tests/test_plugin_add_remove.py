#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from plugin_manager import PluginManager

def test_add_remove_plugin():
    print("=== TEST ADD/REMOVE PLUGIN ===")
    pm = PluginManager()
    print("1. PluginManager créé")
    
    # Ajout
    plugin_data = {
        'module': None,
        'config': {'name': 'test_plugin', 'version': '1.0.0'},
        'path': './test_plugin.py'
    }
    added = pm.add_plugin('test_plugin', plugin_data)
    print(f"2. Ajout du plugin: {'OK' if added else 'ECHEC'}")
    assert added, "add_plugin doit retourner True"
    assert 'test_plugin' in pm.plugins, "Le plugin doit être présent après ajout"
    print(f"   ✓ Plugins après ajout: {list(pm.plugins.keys())}")
    
    # Suppression
    removed = pm.remove_plugin('test_plugin')
    print(f"3. Suppression du plugin: {'OK' if removed else 'ECHEC'}")
    assert removed, "remove_plugin doit retourner True"
    assert 'test_plugin' not in pm.plugins, "Le plugin ne doit plus être présent après suppression"
    print(f"   ✓ Plugins après suppression: {list(pm.plugins.keys())}")
    
    # Suppression d'un plugin inexistant
    removed2 = pm.remove_plugin('inexistant')
    print(f"4. Suppression d'un plugin inexistant: {'OK' if removed2 else 'ECHEC (attendu)'}")
    assert not removed2, "remove_plugin doit retourner False pour un plugin inexistant"
    
    print("\n=== SUCCES! ADD/REMOVE PLUGIN OPERATIONNEL ===")
    return True

if __name__ == "__main__":
    test_add_remove_plugin() 