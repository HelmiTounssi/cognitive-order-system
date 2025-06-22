# Système de Plugins

Ce dossier contient les plugins pour étendre les fonctionnalités du système cognitif.

## Structure d'un Plugin

Un plugin doit suivre cette structure :

```python
class MonPlugin:
    def __init__(self):
        self.name = "mon_plugin"
        self.version = "1.0.0"
        self.description = "Description du plugin"
        self.author = "Auteur"
        self.category = "category"
        
        # Métadonnées
        self.metadata = {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'category': self.category,
            'created_at': datetime.now().isoformat(),
            'dependencies': [],
            'tags': ['tag1', 'tag2']
        }
        
        # Fonctions exposées
        self.functions = {
            'ma_fonction': self.ma_fonction,
            # ... autres fonctions
        }
        
        # Configuration
        self.config = {
            'enabled': True,
            'auto_load': True,
            'settings': {}
        }
    
    def ma_fonction(self, param1, param2):
        """Documentation de la fonction"""
        # Logique de la fonction
        return result
    
    def get_info(self):
        """Retourne les informations du plugin"""
        return {
            'metadata': self.metadata,
            'config': self.config,
            'functions': list(self.functions.keys()),
            'status': 'active' if self.config['enabled'] else 'disabled'
        }

def create_plugin():
    """Fonction de création requise"""
    return MonPlugin()
```

## Plugin d'Exemple

Le fichier `example_plugin.py` contient un plugin complet avec :

- **hello_world()** : Fonction de démonstration simple
- **process_data()** : Traitement de données avec logique métier
- **analyze_text()** : Analyse de texte et extraction d'informations
- **generate_report()** : Génération de rapports (synthèse/détaillé)
- **custom_business_logic()** : Logique métier personnalisée (calcul de remises)

## Utilisation

### Test du plugin d'exemple

```bash
# Test direct du plugin
python plugins/example_plugin.py

# Test complet avec le gestionnaire de plugins
python scripts/test_plugin_example.py
```

### Intégration dans le système

```python
from src.plugin_manager import PluginManager
from plugins.example_plugin import ExamplePlugin

# Créer le gestionnaire
plugin_manager = PluginManager()

# Charger le plugin
plugin_manager.load_plugin("plugins/example_plugin.py")

# Utiliser le plugin
plugin = plugin_manager.get_plugin("example_plugin")
result = plugin.custom_business_logic({
    'amount': 1000,
    'customer_type': 'vip'
})
```

## Création d'un Nouveau Plugin

1. **Créer un nouveau fichier** dans le dossier `plugins/`
2. **Suivre la structure** définie ci-dessus
3. **Implémenter les fonctions** nécessaires
4. **Ajouter la fonction `create_plugin()`**
5. **Tester le plugin** avec le script de test

## Bonnes Pratiques

- **Nommage** : Utiliser des noms descriptifs (ex: `ecommerce_plugin.py`)
- **Documentation** : Documenter toutes les fonctions
- **Gestion d'erreurs** : Gérer les cas d'erreur
- **Configuration** : Permettre la configuration via `self.config`
- **Tests** : Inclure des tests dans le plugin

## Exemples d'Utilisation

### Plugin E-commerce
```python
# Calcul de remises, gestion des stocks, etc.
```

### Plugin Analytics
```python
# Analyse de données, génération de rapports, etc.
```

### Plugin Communication
```python
# Envoi d'emails, notifications, etc.
```

## Support

Pour créer un nouveau plugin ou obtenir de l'aide, consultez :
- Le plugin d'exemple (`example_plugin.py`)
- Le script de test (`scripts/test_plugin_example.py`)
- La documentation du `PluginManager` dans `src/plugin_manager.py` 