"""
Interface d'Administration Sémantique
Permet à un non-développeur de configurer le système via une interface simple
"""

import os
import json
import yaml
from typing import Dict, List, Optional
from knowledge_base import KnowledgeBase
from plugin_manager import PluginManager


class AdminInterface:
    """
    Interface d'administration pour configurer le système sémantique
    """
    
    def __init__(self, knowledge_base: KnowledgeBase, plugin_manager: PluginManager):
        """
        Initialise l'interface d'administration
        
        Args:
            knowledge_base: Instance de la base de connaissances
            plugin_manager: Instance du gestionnaire de plug-ins
        """
        self.kb = knowledge_base
        self.plugin_manager = plugin_manager
        self.config_directory = "./admin_config"
        
        # Crée le répertoire de configuration s'il n'existe pas
        if not os.path.exists(self.config_directory):
            os.makedirs(self.config_directory)
            print(f"📁 Répertoire de configuration créé: {self.config_directory}")
    
    def show_main_menu(self):
        """Affiche le menu principal de l'interface d'administration"""
        while True:
            print("\n" + "="*60)
            print("🧠 INTERFACE D'ADMINISTRATION SÉMANTIQUE")
            print("="*60)
            print("1. 📚 Gérer l'ontologie")
            print("2. 🔌 Gérer les plug-ins")
            print("3. 🎯 Gérer les handlers métiers")
            print("4. ⚙️  Configuration système")
            print("5. 📊 Statistiques et monitoring")
            print("6. 💾 Sauvegarder/Restaurer")
            print("0. 🚪 Quitter")
            print("-"*60)
            
            choice = input("Votre choix (0-6): ").strip()
            
            if choice == "1":
                self.ontology_menu()
            elif choice == "2":
                self.plugins_menu()
            elif choice == "3":
                self.handlers_menu()
            elif choice == "4":
                self.system_config_menu()
            elif choice == "5":
                self.stats_menu()
            elif choice == "6":
                self.backup_menu()
            elif choice == "0":
                print("👋 Au revoir!")
                break
            else:
                print("❌ Choix invalide. Veuillez réessayer.")
    
    def ontology_menu(self):
        """Menu de gestion de l'ontologie"""
        while True:
            print("\n" + "="*50)
            print("📚 GESTION DE L'ONTOLOGIE")
            print("="*50)
            print("1. 🔍 Introspection de l'ontologie")
            print("2. ➕ Ajouter une nouvelle classe")
            print("3. 🏗️  Ajouter des propriétés à une classe")
            print("4. 📝 Créer une instance")
            print("5. 🔗 Lier des instances")
            print("6. 📋 Lister les classes")
            print("7. 📋 Lister les instances")
            print("0. ⬅️  Retour")
            print("-"*50)
            
            choice = input("Votre choix (0-7): ").strip()
            
            if choice == "1":
                self.introspect_ontology()
            elif choice == "2":
                self.add_class_interactive()
            elif choice == "3":
                self.add_properties_interactive()
            elif choice == "4":
                self.create_instance_interactive()
            elif choice == "5":
                self.link_instances_interactive()
            elif choice == "6":
                self.list_classes()
            elif choice == "7":
                self.list_instances()
            elif choice == "0":
                break
            else:
                print("❌ Choix invalide.")
    
    def introspect_ontology(self):
        """Affiche l'introspection de l'ontologie"""
        print("\n🔍 INTROSPECTION DE L'ONTOLOGIE")
        print("-"*40)
        
        ontology_info = self.kb.introspect_ontology()
        
        print(f"📊 Classes: {len(ontology_info.get('classes', []))}")
        for class_info in ontology_info['classes']:
            print(f"   - {class_info['name']}: {class_info['instances_count']} instances")
        
        print(f"\n📊 Propriétés: {len(ontology_info.get('properties', []))}")
        for prop_info in ontology_info['properties']:
            print(f"   - {prop_info['name']} ({prop_info['type']}): {prop_info['range']}")
        
        print(f"\n📊 Namespaces: {len(ontology_info.get('namespaces', []))}")
        for ns_info in ontology_info['namespaces']:
            print(f"   - {ns_info['prefix']}: {ns_info['uri']}")
    
    def add_class_interactive(self):
        """Ajoute une classe de manière interactive"""
        print("\n➕ AJOUTER UNE NOUVELLE CLASSE")
        print("-"*40)
        
        class_name = input("Nom de la classe: ").strip()
        if not class_name:
            print("❌ Nom de classe requis.")
            return
        
        description = input("Description (optionnel): ").strip()
        
        # Ajout des propriétés
        properties = []
        print("\nAjout des propriétés (laissez vide pour terminer):")
        
        while True:
            prop_name = input("Nom de la propriété (ex: hasName): ").strip()
            if not prop_name:
                break
            
            prop_type = input("Type (string/float/int/boolean/class): ").strip()
            prop_label = input("Label (optionnel): ").strip()
            
            properties.append({
                'name': prop_name,
                'type': prop_type,
                'label': prop_label or prop_name
            })
        
        # Création de la classe
        success = self.kb.extend_ontology_dynamically(class_name, properties)
        
        if success:
            print(f"✅ Classe '{class_name}' ajoutée avec succès!")
        else:
            print(f"❌ Erreur lors de l'ajout de la classe '{class_name}'")
    
    def add_properties_interactive(self):
        """Ajoute des propriétés à une classe existante"""
        print("\n🏗️  AJOUTER DES PROPRIÉTÉS À UNE CLASSE")
        print("-"*40)
        
        # Liste les classes disponibles
        classes = self.kb.query_ontology_introspectively('classes')
        if not classes:
            print("❌ Aucune classe disponible.")
            return
        
        print("Classes disponibles:")
        for i, class_info in enumerate(classes, 1):
            print(f"   {i}. {class_info['name']}")
        
        try:
            choice = int(input("\nChoisissez une classe (numéro): ")) - 1
            if choice < 0 or choice >= len(classes):
                print("❌ Choix invalide.")
                return
            
            class_name = classes[choice]['name']
            print(f"\nAjout de propriétés à la classe '{class_name}'")
            
            # Ajout des propriétés
            properties = []
            while True:
                prop_name = input("Nom de la propriété (vide pour terminer): ").strip()
                if not prop_name:
                    break
                
                prop_type = input("Type (string/float/int/boolean/class): ").strip()
                prop_label = input("Label (optionnel): ").strip()
                
                properties.append({
                    'name': prop_name,
                    'type': prop_type,
                    'label': prop_label or prop_name
                })
            
            if properties:
                # Note: Cette fonctionnalité nécessiterait une extension de la KB
                print("⚠️ Fonctionnalité d'ajout de propriétés à implémenter")
                print(f"Propriétés à ajouter: {properties}")
        
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
    
    def create_instance_interactive(self):
        """Crée une instance de manière interactive"""
        print("\n📝 CRÉER UNE INSTANCE")
        print("-"*40)
        
        # Liste les classes disponibles
        classes = self.kb.query_ontology_introspectively('classes')
        if not classes:
            print("❌ Aucune classe disponible.")
            return
        
        print("Classes disponibles:")
        for i, class_info in enumerate(classes, 1):
            print(f"   {i}. {class_info['name']}")
        
        try:
            choice = int(input("\nChoisissez une classe (numéro): ")) - 1
            if choice < 0 or choice >= len(classes):
                print("❌ Choix invalide.")
                return
            
            class_name = classes[choice]['name']
            print(f"\nCréez une instance de la classe '{class_name}'")
            
            # Saisie des propriétés
            properties = {}
            while True:
                prop_name = input("Nom de la propriété (vide pour terminer): ").strip()
                if not prop_name:
                    break
                
                prop_value = input(f"Valeur pour {prop_name}: ").strip()
                properties[prop_name] = prop_value
            
            if properties:
                instance_id = self.kb.create_instance_dynamically(class_name, properties)
                if instance_id:
                    print(f"✅ Instance '{instance_id}' créée avec succès!")
                else:
                    print("❌ Erreur lors de la création de l'instance.")
        
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
    
    def link_instances_interactive(self):
        """Lie des instances de manière interactive"""
        print("\n🔗 LIER DES INSTANCES")
        print("-"*40)
        print("⚠️ Fonctionnalité de liaison d'instances à implémenter")
    
    def list_classes(self):
        """Liste toutes les classes"""
        print("\n📋 LISTE DES CLASSES")
        print("-"*40)
        
        classes = self.kb.query_ontology_introspectively('classes')
        if not classes:
            print("❌ Aucune classe trouvée.")
            return
        
        for i, class_info in enumerate(classes, 1):
            print(f"{i}. {class_info['name']}")
            print(f"   URI: {class_info['uri']}")
            print(f"   Instances: {class_info['instances_count']}")
            print()
    
    def list_instances(self):
        """Liste toutes les instances"""
        print("\n📋 LISTE DES INSTANCES")
        print("-"*40)
        
        instances = self.kb.query_ontology_introspectively('instances')
        if not instances:
            print("❌ Aucune instance trouvée.")
            return
        
        for i, instance_info in enumerate(instances, 1):
            print(f"{i}. {instance_info['id']} ({instance_info['class']})")
            for prop_name, prop_value in instance_info['properties'].items():
                print(f"   {prop_name}: {prop_value}")
            print()
    
    def plugins_menu(self):
        """Menu de gestion des plug-ins"""
        while True:
            print("\n" + "="*50)
            print("🔌 GESTION DES PLUG-INS")
            print("="*50)
            print("1. 📋 Lister les plug-ins")
            print("2. ➕ Créer un template de plug-in")
            print("3. 🔄 Recharger un plug-in")
            print("4. 🗑️  Décharger un plug-in")
            print("5. 🧪 Tester un plug-in")
            print("0. ⬅️  Retour")
            print("-"*50)
            
            choice = input("Votre choix (0-5): ").strip()
            
            if choice == "1":
                self.list_plugins()
            elif choice == "2":
                self.create_plugin_template()
            elif choice == "3":
                self.reload_plugin()
            elif choice == "4":
                self.unload_plugin()
            elif choice == "5":
                self.test_plugin()
            elif choice == "0":
                break
            else:
                print("❌ Choix invalide.")
    
    def list_plugins(self):
        """Liste tous les plug-ins"""
        print("\n📋 LISTE DES PLUG-INS")
        print("-"*40)
        
        plugins = self.plugin_manager.list_plugins()
        if not plugins:
            print("❌ Aucun plug-in chargé.")
            return
        
        for i, plugin_info in enumerate(plugins, 1):
            print(f"{i}. {plugin_info['name']}")
            print(f"   Version: {plugin_info['config'].get('version', 'N/A')}")
            print(f"   Description: {plugin_info['config'].get('description', 'N/A')}")
            print(f"   Auteur: {plugin_info['config'].get('author', 'N/A')}")
            print()
    
    def create_plugin_template(self):
        """Crée un template de plug-in"""
        print("\n➕ CRÉER UN TEMPLATE DE PLUG-IN")
        print("-"*40)
        
        plugin_name = input("Nom du plug-in: ").strip()
        if not plugin_name:
            print("❌ Nom de plug-in requis.")
            return
        
        print("Type de template:")
        print("1. Répertoire (recommandé)")
        print("2. Fichier simple")
        
        choice = input("Votre choix (1-2): ").strip()
        
        if choice == "1":
            plugin_type = "directory"
        elif choice == "2":
            plugin_type = "file"
        else:
            print("❌ Choix invalide.")
            return
        
        success = self.plugin_manager.create_plugin_template(plugin_name, plugin_type)
        
        if success:
            print(f"✅ Template de plug-in '{plugin_name}' créé avec succès!")
        else:
            print(f"❌ Erreur lors de la création du template.")
    
    def reload_plugin(self):
        """Recharge un plug-in"""
        print("\n🔄 RECHARGER UN PLUG-IN")
        print("-"*40)
        
        plugins = self.plugin_manager.list_plugins()
        if not plugins:
            print("❌ Aucun plug-in chargé.")
            return
        
        print("Plug-ins disponibles:")
        for i, plugin_info in enumerate(plugins, 1):
            print(f"   {i}. {plugin_info['name']}")
        
        try:
            choice = int(input("\nChoisissez un plug-in (numéro): ")) - 1
            if choice < 0 or choice >= len(plugins):
                print("❌ Choix invalide.")
                return
            
            plugin_name = plugins[choice]['name']
            success = self.plugin_manager.reload_plugin(plugin_name)
            
            if success:
                print(f"✅ Plug-in '{plugin_name}' rechargé avec succès!")
            else:
                print(f"❌ Erreur lors du rechargement.")
        
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
    
    def unload_plugin(self):
        """Décharge un plug-in"""
        print("\n🗑️  DÉCHARGER UN PLUG-IN")
        print("-"*40)
        
        plugins = self.plugin_manager.list_plugins()
        if not plugins:
            print("❌ Aucun plug-in chargé.")
            return
        
        print("Plug-ins disponibles:")
        for i, plugin_info in enumerate(plugins, 1):
            print(f"   {i}. {plugin_info['name']}")
        
        try:
            choice = int(input("\nChoisissez un plug-in (numéro): ")) - 1
            if choice < 0 or choice >= len(plugins):
                print("❌ Choix invalide.")
                return
            
            plugin_name = plugins[choice]['name']
            success = self.plugin_manager.unload_plugin(plugin_name)
            
            if success:
                print(f"✅ Plug-in '{plugin_name}' déchargé avec succès!")
            else:
                print(f"❌ Erreur lors du déchargement.")
        
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
    
    def test_plugin(self):
        """Teste un plug-in"""
        print("\n🧪 TESTER UN PLUG-IN")
        print("-"*40)
        
        plugins = self.plugin_manager.list_plugins()
        if not plugins:
            print("❌ Aucun plug-in chargé.")
            return
        
        print("Plug-ins disponibles:")
        for i, plugin_info in enumerate(plugins, 1):
            print(f"   {i}. {plugin_info['name']}")
        
        try:
            choice = int(input("\nChoisissez un plug-in (numéro): ")) - 1
            if choice < 0 or choice >= len(plugins):
                print("❌ Choix invalide.")
                return
            
            plugin_name = plugins[choice]['name']
            print(f"\nTest du plug-in '{plugin_name}'")
            
            # Test avec des paramètres simples
            test_params = {'test_param': 'test_value', 'user': 'admin'}
            
            try:
                result = self.plugin_manager.execute_plugin_method(
                    plugin_name, 'handle_request', test_params
                )
                print(f"✅ Test réussi: {result}")
            except Exception as e:
                print(f"❌ Test échoué: {e}")
        
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
    
    def handlers_menu(self):
        """Menu de gestion des handlers métiers"""
        while True:
            print("\n" + "="*50)
            print("🎯 GESTION DES HANDLERS MÉTIERS")
            print("="*50)
            print("1. 📋 Lister les handlers")
            print("2. ➕ Ajouter un handler")
            print("3. 🔍 Voir la configuration d'un handler")
            print("4. 🧪 Tester un handler")
            print("5. 🗑️  Supprimer un handler")
            print("0. ⬅️  Retour")
            print("-"*50)
            
            choice = input("Votre choix (0-5): ").strip()
            
            if choice == "1":
                self.list_handlers()
            elif choice == "2":
                self.add_handler_interactive()
            elif choice == "3":
                self.view_handler_config()
            elif choice == "4":
                self.test_handler()
            elif choice == "5":
                self.delete_handler()
            elif choice == "0":
                break
            else:
                print("❌ Choix invalide.")
    
    def list_handlers(self):
        """Liste tous les handlers métiers"""
        print("\n📋 LISTE DES HANDLERS MÉTIERS")
        print("-"*40)
        
        handlers = self.kb.list_business_handlers()
        if not handlers:
            print("❌ Aucun handler métier trouvé.")
            return
        
        for i, handler_info in enumerate(handlers, 1):
            print(f"{i}. {handler_info['intent_name']}")
            print(f"   Description: {handler_info.get('description', 'N/A')}")
            print()
    
    def add_handler_interactive(self):
        """Ajoute un handler métier de manière interactive"""
        print("\n➕ AJOUTER UN HANDLER MÉTIER")
        print("-"*40)
        
        intent_name = input("Nom de l'intention (ex: create_order): ").strip()
        if not intent_name:
            print("❌ Nom d'intention requis.")
            return
        
        description = input("Description du handler: ").strip()
        
        # Configuration du handler
        handler_config = {
            'description': description,
            'extraction_patterns': {},
            'workflow': [],
            'rules': []
        }
        
        # Patterns d'extraction
        print("\nAjout des patterns d'extraction (laissez vide pour terminer):")
        while True:
            param_name = input("Nom du paramètre (ex: client_name): ").strip()
            if not param_name:
                break
            
            patterns = []
            print(f"Patterns pour {param_name} (laissez vide pour terminer):")
            while True:
                pattern = input("Pattern regex: ").strip()
                if not pattern:
                    break
                patterns.append(pattern)
            
            if patterns:
                handler_config['extraction_patterns'][param_name] = patterns
        
        # Workflow
        print("\nAjout du workflow (laissez vide pour terminer):")
        step_num = 1
        while True:
            action = input(f"Action pour l'étape {step_num}: ").strip()
            if not action:
                break
            
            params_input = input("Paramètres (séparés par des virgules): ").strip()
            params = [p.strip() for p in params_input.split(',') if p.strip()]
            
            handler_config['workflow'].append({
                'step': step_num,
                'action': action,
                'params': params
            })
            step_num += 1
        
        # Règles
        print("\nAjout des règles métier (laissez vide pour terminer):")
        while True:
            condition = input("Condition (ex: stock_insufficient): ").strip()
            if not condition:
                break
            
            action = input("Action (ex: suggest_alternatives): ").strip()
            
            handler_config['rules'].append({
                'condition': condition,
                'action': action
            })
        
        # Ajout du handler
        success = self.kb.add_business_handler(intent_name, handler_config)
        
        if success:
            print(f"✅ Handler métier '{intent_name}' ajouté avec succès!")
        else:
            print(f"❌ Erreur lors de l'ajout du handler.")
    
    def view_handler_config(self):
        """Affiche la configuration d'un handler"""
        print("\n🔍 VOIR LA CONFIGURATION D'UN HANDLER")
        print("-"*40)
        
        handlers = self.kb.list_business_handlers()
        if not handlers:
            print("❌ Aucun handler trouvé.")
            return
        
        print("Handlers disponibles:")
        for i, handler_info in enumerate(handlers, 1):
            print(f"   {i}. {handler_info['intent_name']}")
        
        try:
            choice = int(input("\nChoisissez un handler (numéro): ")) - 1
            if choice < 0 or choice >= len(handlers):
                print("❌ Choix invalide.")
                return
            
            intent_name = handlers[choice]['intent_name']
            config = self.kb.get_business_handler(intent_name)
            
            if config:
                print(f"\nConfiguration du handler '{intent_name}':")
                print(f"Description: {config.get('description', 'N/A')}")
                
                print(f"\nPatterns d'extraction:")
                for param, patterns in config.get('extraction_patterns', {}).items():
                    print(f"  {param}: {patterns}")
                
                print(f"\nWorkflow:")
                for step in config.get('workflow', []):
                    print(f"  Étape {step['step']}: {step['action']} ({step['params']})")
                
                print(f"\nRègles:")
                for rule in config.get('rules', []):
                    print(f"  Si {rule['condition']} alors {rule['action']}")
            else:
                print("❌ Configuration non trouvée.")
        
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
    
    def test_handler(self):
        """Teste un handler métier"""
        print("\n🧪 TESTER UN HANDLER MÉTIER")
        print("-"*40)
        
        handlers = self.kb.list_business_handlers()
        if not handlers:
            print("❌ Aucun handler trouvé.")
            return
        
        print("Handlers disponibles:")
        for i, handler_info in enumerate(handlers, 1):
            print(f"   {i}. {handler_info['intent_name']}")
        
        try:
            choice = int(input("\nChoisissez un handler (numéro): ")) - 1
            if choice < 0 or choice >= len(handlers):
                print("❌ Choix invalide.")
                return
            
            intent_name = handlers[choice]['intent_name']
            print(f"\nTest du handler '{intent_name}'")
            
            # Paramètres de test
            test_params = {'test_param': 'test_value'}
            
            success, result = self.kb.execute_business_workflow(intent_name, test_params)
            
            if success:
                print(f"✅ Test réussi: {result}")
            else:
                print(f"❌ Test échoué: {result}")
        
        except ValueError:
            print("❌ Veuillez entrer un numéro valide.")
    
    def delete_handler(self):
        """Supprime un handler métier"""
        print("\n🗑️  SUPPRIMER UN HANDLER MÉTIER")
        print("-"*40)
        print("⚠️ Fonctionnalité de suppression à implémenter")
    
    def system_config_menu(self):
        """Menu de configuration système"""
        print("\n" + "="*50)
        print("⚙️  CONFIGURATION SYSTÈME")
        print("="*50)
        print("⚠️ Interface de configuration système à implémenter")
    
    def stats_menu(self):
        """Menu de statistiques et monitoring"""
        print("\n" + "="*50)
        print("📊 STATISTIQUES ET MONITORING")
        print("="*50)
        print("⚠️ Interface de monitoring à implémenter")
    
    def backup_menu(self):
        """Menu de sauvegarde et restauration"""
        print("\n" + "="*50)
        print("💾 SAUVEGARDE ET RESTAURATION")
        print("="*50)
        print("⚠️ Interface de sauvegarde à implémenter")
