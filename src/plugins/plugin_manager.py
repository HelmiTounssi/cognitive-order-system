"""
Gestionnaire de Plug-ins Dynamiques
Permet de charger des modules Python à chaud pour des besoins métier avancés
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Optional, Any
import json
import yaml


class PluginManager:
    """
    Gestionnaire de plug-ins pour charger dynamiquement des modules Python
    """
    
    def __init__(self, plugins_directory: str = "./plugins"):
        """
        Initialise le gestionnaire de plug-ins
        
        Args:
            plugins_directory: Répertoire contenant les plug-ins
        """
        self.plugins_directory = plugins_directory
        self.loaded_plugins = {}
        self.plugin_configs = {}
        
        # Crée le répertoire des plug-ins s'il n'existe pas
        if not os.path.exists(plugins_directory):
            os.makedirs(plugins_directory)
            print(f"📁 Répertoire des plug-ins créé: {plugins_directory}")
        
        # Charge automatiquement les plug-ins au démarrage
        self.discover_and_load_plugins()
    
    def discover_and_load_plugins(self) -> List[str]:
        """
        Découvre et charge automatiquement tous les plug-ins disponibles
        
        Returns:
            List[str]: Liste des noms de plug-ins chargés
        """
        loaded = []
        
        if not os.path.exists(self.plugins_directory):
            return loaded
        
        for item in os.listdir(self.plugins_directory):
            item_path = os.path.join(self.plugins_directory, item)
            
            if os.path.isdir(item_path):
                # Plug-in sous forme de répertoire
                plugin_name = item
                config_file = os.path.join(item_path, "plugin_config.yaml")
                
                if os.path.exists(config_file):
                    if self.load_plugin_from_directory(plugin_name, item_path):
                        loaded.append(plugin_name)
            
            elif item.endswith('.py') and not item.startswith('__'):
                # Plug-in sous forme de fichier Python
                plugin_name = item[:-3]  # Enlève l'extension .py
                if self.load_plugin_from_file(plugin_name, item_path):
                    loaded.append(plugin_name)
        
        print(f"🔌 {len(loaded)} plug-ins découverts et chargés: {loaded}")
        return loaded
    
    def load_plugin_from_directory(self, plugin_name: str, plugin_path: str) -> bool:
        """
        Charge un plug-in depuis un répertoire
        
        Args:
            plugin_name: Nom du plug-in
            plugin_path: Chemin vers le répertoire du plug-in
        
        Returns:
            bool: True si succès
        """
        try:
            config_file = os.path.join(plugin_path, "plugin_config.yaml")
            main_file = os.path.join(plugin_path, "main.py")
            
            if not os.path.exists(config_file) or not os.path.exists(main_file):
                print(f"⚠️ Plug-in '{plugin_name}' incomplet (config.yaml ou main.py manquant)")
                return False
            
            # Charge la configuration
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Charge le module principal
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}", main_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Enregistre le plug-in
            self.loaded_plugins[plugin_name] = {
                'module': module,
                'config': config,
                'path': plugin_path
            }
            
            print(f"✅ Plug-in '{plugin_name}' chargé depuis le répertoire")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du plug-in '{plugin_name}': {e}")
            return False
    
    def load_plugin_from_file(self, plugin_name: str, plugin_path: str) -> bool:
        """
        Charge un plug-in depuis un fichier Python
        
        Args:
            plugin_name: Nom du plug-in
            plugin_path: Chemin vers le fichier Python
        
        Returns:
            bool: True si succès
        """
        try:
            # Charge le module
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}", plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Configuration par défaut
            config = {
                'name': plugin_name,
                'version': '1.0.0',
                'description': f'Plug-in {plugin_name}',
                'author': 'Unknown',
                'entry_points': []
            }
            
            # Essaie de récupérer la configuration depuis le module
            if hasattr(module, 'PLUGIN_CONFIG'):
                config.update(module.PLUGIN_CONFIG)
            
            # Enregistre le plug-in
            self.loaded_plugins[plugin_name] = {
                'module': module,
                'config': config,
                'path': plugin_path
            }
            
            print(f"✅ Plug-in '{plugin_name}' chargé depuis le fichier")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement du plug-in '{plugin_name}': {e}")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Dict]:
        """
        Récupère un plug-in chargé
        
        Args:
            plugin_name: Nom du plug-in
        
        Returns:
            Optional[Dict]: Informations du plug-in ou None
        """
        return self.loaded_plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict]:
        """
        Liste tous les plug-ins chargés
        
        Returns:
            List[Dict]: Liste des plug-ins avec leurs informations
        """
        plugins_info = []
        
        for name, plugin_data in self.loaded_plugins.items():
            info = {
                'name': name,
                'config': plugin_data['config'],
                'path': plugin_data['path']
            }
            plugins_info.append(info)
        
        return plugins_info
    
    @property
    def plugins(self) -> Dict:
        """
        Propriété pour accéder aux plug-ins chargés
        
        Returns:
            Dict: Dictionnaire des plug-ins chargés
        """
        return self.loaded_plugins
    
    def add_plugin(self, name: str, plugin_data: dict) -> bool:
        """
        Ajoute dynamiquement un plug-in au gestionnaire (usage test/dynamique)
        Args:
            name: Nom du plug-in
            plugin_data: Dictionnaire du plug-in (doit contenir au moins 'module' et 'config')
        Returns:
            bool: True si succès, False sinon
        """
        if not isinstance(plugin_data, dict):
            print(f"❌ plugin_data doit être un dictionnaire")
            return False
        self.loaded_plugins[name] = plugin_data
        return True

    def remove_plugin(self, name: str) -> bool:
        """
        Supprime un plug-in du gestionnaire
        Args:
            name: Nom du plug-in à supprimer
        Returns:
            bool: True si succès, False sinon
        """
        if name in self.loaded_plugins:
            del self.loaded_plugins[name]
            return True
        print(f"❌ Plug-in '{name}' non trouvé")
        return False
    
    def execute_plugin_method(self, plugin_name: str, method_name: str, 
                            *args, **kwargs) -> Any:
        """
        Exécute une méthode d'un plug-in
        
        Args:
            plugin_name: Nom du plug-in
            method_name: Nom de la méthode à exécuter
            *args: Arguments positionnels
            **kwargs: Arguments nommés
        
        Returns:
            Any: Résultat de l'exécution
        """
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plug-in '{plugin_name}' non trouvé")
        
        module = plugin['module']
        if not hasattr(module, method_name):
            raise AttributeError(f"Méthode '{method_name}' non trouvée dans le plug-in '{plugin_name}'")
        
        method = getattr(module, method_name)
        return method(*args, **kwargs)
    
    def create_plugin_template(self, plugin_name: str, plugin_type: str = "directory") -> bool:
        """
        Crée un template de plug-in
        
        Args:
            plugin_name: Nom du plug-in
            plugin_type: Type de template ('directory' ou 'file')
        
        Returns:
            bool: True si succès
        """
        try:
            if plugin_type == "directory":
                return self._create_directory_plugin_template(plugin_name)
            elif plugin_type == "file":
                return self._create_file_plugin_template(plugin_name)
            else:
                raise ValueError(f"Type de plug-in inconnu: {plugin_type}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la création du template: {e}")
            return False
    
    def _create_directory_plugin_template(self, plugin_name: str) -> bool:
        """Crée un template de plug-in sous forme de répertoire"""
        plugin_path = os.path.join(self.plugins_directory, plugin_name)
        
        if os.path.exists(plugin_path):
            print(f"⚠️ Le répertoire '{plugin_path}' existe déjà")
            return False
        
        # Crée le répertoire
        os.makedirs(plugin_path)
        
        # Crée le fichier de configuration
        config_content = f"""# Configuration du plug-in {plugin_name}
name: {plugin_name}
version: 1.0.0
description: Description du plug-in {plugin_name}
author: Votre nom
entry_points:
  - name: main_handler
    method: handle_request
    description: Point d'entrée principal du plug-in
"""
        
        with open(os.path.join(plugin_path, "plugin_config.yaml"), 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Crée le fichier principal
        main_content = f'''"""
Plug-in {plugin_name}
Module principal du plug-in
"""

def handle_request(params):
    """
    Point d'entrée principal du plug-in
    
    Args:
        params: Paramètres de la requête
    
    Returns:
        str: Résultat du traitement
    """
    return f"Plug-in {plugin_name} traite la requête avec les paramètres: {{params}}"

def initialize_plugin():
    """Initialise le plug-in"""
    print(f"🔌 Plug-in {plugin_name} initialisé")

def cleanup_plugin():
    """Nettoie le plug-in"""
    print(f"🧹 Plug-in {plugin_name} nettoyé")

# Configuration du plug-in
PLUGIN_CONFIG = {{
    'name': '{plugin_name}',
    'version': '1.0.0',
    'description': 'Description du plug-in {plugin_name}',
    'author': 'Votre nom'
}}
'''
        
        with open(os.path.join(plugin_path, "main.py"), 'w', encoding='utf-8') as f:
            f.write(main_content)
        
        # Crée un fichier README
        readme_content = f"""# Plug-in {plugin_name}

## Description
Description du plug-in {plugin_name}

## Installation
Ce plug-in est automatiquement découvert et chargé par le PluginManager.

## Utilisation
```python
# Exécuter une méthode du plug-in
result = plugin_manager.execute_plugin_method('{plugin_name}', 'handle_request', {{'param': 'value'}})
```

## Configuration
Modifiez le fichier `plugin_config.yaml` pour configurer le plug-in.
"""
        
        with open(os.path.join(plugin_path, "README.md"), 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ Template de plug-in '{plugin_name}' créé dans {plugin_path}")
        return True
    
    def _create_file_plugin_template(self, plugin_name: str) -> bool:
        """Crée un template de plug-in sous forme de fichier"""
        plugin_file = os.path.join(self.plugins_directory, f"{plugin_name}.py")
        
        if os.path.exists(plugin_file):
            print(f"⚠️ Le fichier '{plugin_file}' existe déjà")
            return False
        
        # Crée le fichier de plug-in
        content = f'''"""
Plug-in {plugin_name}
Plug-in simple sous forme de fichier Python
"""

def handle_request(params):
    """
    Point d'entrée principal du plug-in
    
    Args:
        params: Paramètres de la requête
    
    Returns:
        str: Résultat du traitement
    """
    return f"Plug-in {plugin_name} traite la requête avec les paramètres: {{params}}"

def custom_method(param1, param2=None):
    """
    Méthode personnalisée du plug-in
    
    Args:
        param1: Premier paramètre
        param2: Deuxième paramètre (optionnel)
    
    Returns:
        str: Résultat
    """
    return f"Résultat: {{param1}} - {{param2}}"

# Configuration du plug-in
PLUGIN_CONFIG = {{
    'name': '{plugin_name}',
    'version': '1.0.0',
    'description': 'Plug-in simple {plugin_name}',
    'author': 'Votre nom',
    'entry_points': [
        {{
            'name': 'handle_request',
            'method': 'handle_request',
            'description': 'Point d\'entrée principal'
        }},
        {{
            'name': 'custom_method',
            'method': 'custom_method',
            'description': 'Méthode personnalisée'
        }}
    ]
}}
'''
        
        with open(plugin_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Template de plug-in '{plugin_name}' créé: {plugin_file}")
        return True
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Recharge un plug-in
        
        Args:
            plugin_name: Nom du plug-in
        
        Returns:
            bool: True si succès
        """
        try:
            plugin = self.get_plugin(plugin_name)
            if not plugin:
                return False
            
            # Supprime le module du cache
            if plugin_name in sys.modules:
                del sys.modules[f"plugins.{plugin_name}"]
            
            # Recharge le plug-in
            if os.path.isdir(plugin['path']):
                return self.load_plugin_from_directory(plugin_name, plugin['path'])
            else:
                return self.load_plugin_from_file(plugin_name, plugin['path'])
                
        except Exception as e:
            print(f"❌ Erreur lors du rechargement du plug-in '{plugin_name}': {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Décharge un plug-in
        
        Args:
            plugin_name: Nom du plug-in
        
        Returns:
            bool: True si succès
        """
        try:
            if plugin_name not in self.loaded_plugins:
                return False
            
            # Appelle la méthode de nettoyage si elle existe
            plugin = self.loaded_plugins[plugin_name]
            module = plugin['module']
            
            if hasattr(module, 'cleanup_plugin'):
                module.cleanup_plugin()
            
            # Supprime le module du cache
            if f"plugins.{plugin_name}" in sys.modules:
                del sys.modules[f"plugins.{plugin_name}"]
            
            # Supprime le plug-in de la liste
            del self.loaded_plugins[plugin_name]
            
            print(f"✅ Plug-in '{plugin_name}' déchargé")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du déchargement du plug-in '{plugin_name}': {e}")
            return False 