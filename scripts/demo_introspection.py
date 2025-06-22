#!/usr/bin/env python3
"""
Démo d'introspection du système
Permet de tester la réflexion et l'introspection sur l'ontologie
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.knowledge_base import KnowledgeBase
import tools
import json

def demo_introspection():
    """Démonstration de l'introspection de l'ontologie"""
    print("🔍 DÉMONSTRATION D'INTROSPECTION DE L'ONTOLOGIE")
    print("=" * 50)
    
    # Initialise la base de connaissances
    kb = KnowledgeBase()
    
    # 1. Introspection complète
    print("\n1. Introspection complète de l'ontologie:")
    ontology_info = kb.introspect_ontology()
    
    print(f"📊 Classes trouvées: {len(ontology_info.get('classes', []))}")
    for class_info in ontology_info['classes']:
        print(f"   - {class_info['name']}: {class_info['instances_count']} instances")
    
    print(f"\n📊 Propriétés trouvées: {len(ontology_info.get('properties', []))}")
    for prop_info in ontology_info['properties']:
        print(f"   - {prop_info['name']} ({prop_info['type']}): {prop_info['range']}")
    
    # 2. Requêtes introspectives
    print("\n2. Requêtes introspectives:")
    
    # Requête des classes
    classes = kb.query_ontology_introspectively('classes')
    print(f"   Classes: {len(classes)} trouvées")
    
    # Requête des propriétés
    properties = kb.query_ontology_introspectively('properties')
    print(f"   Propriétés: {len(properties)} trouvées")
    
    # Requête des instances
    instances = kb.query_ontology_introspectively('instances')
    print(f"   Instances: {len(instances)} trouvées")

def demo_extension_dynamique():
    """Démonstration de l'extension dynamique de l'ontologie"""
    print("\n\n🆕 DÉMONSTRATION D'EXTENSION DYNAMIQUE")
    print("=" * 50)
    
    # Initialise la base de connaissances
    kb = KnowledgeBase()
    
    # 1. Création d'une nouvelle classe "Service"
    print("\n1. Création d'une nouvelle classe 'Service':")
    
    service_properties = [
        {'name': 'hasName', 'type': 'string', 'label': 'Nom du service'},
        {'name': 'hasDescription', 'type': 'string', 'label': 'Description du service'},
        {'name': 'hasPrice', 'type': 'float', 'label': 'Prix du service'},
        {'name': 'hasDuration', 'type': 'int', 'label': 'Durée en heures'},
        {'name': 'hasCategory', 'type': 'string', 'label': 'Catégorie du service'}
    ]
    
    success = kb.extend_ontology_dynamically('Service', service_properties)
    print(f"   Résultat: {'✅ Succès' if success else '❌ Échec'}")
    
    # 2. Création d'instances de la nouvelle classe
    print("\n2. Création d'instances de la classe 'Service':")
    
    # Instance 1
    service1_properties = {
        'hasName': 'Maintenance informatique',
        'hasDescription': 'Service de maintenance préventive et curative',
        'hasPrice': 150.0,
        'hasDuration': 4,
        'hasCategory': 'Maintenance'
    }
    
    instance1_id = kb.create_instance_dynamically('Service', service1_properties)
    print(f"   Instance 1: {instance1_id}")
    
    # Instance 2
    service2_properties = {
        'hasName': 'Formation utilisateur',
        'hasDescription': 'Formation sur les outils informatiques',
        'hasPrice': 200.0,
        'hasDuration': 8,
        'hasCategory': 'Formation'
    }
    
    instance2_id = kb.create_instance_dynamically('Service', service2_properties)
    print(f"   Instance 2: {instance2_id}")
    
    # 3. Vérification de l'extension
    print("\n3. Vérification de l'extension:")
    
    # Nouvelle introspection
    ontology_info = kb.introspect_ontology()
    print(f"   Classes après extension: {len(ontology_info.get('classes', []))}")
    
    # Recherche de la nouvelle classe
    for class_info in ontology_info['classes']:
        if class_info['name'] == 'Service':
            print(f"   ✅ Classe 'Service' trouvée avec {class_info['instances_count']} instances")
            break
    
    # Requête des instances de la nouvelle classe
    service_instances = kb.query_ontology_introspectively('instances', class_name='Service')
    print(f"   Instances de Service: {len(service_instances)}")
    for instance in service_instances:
        print(f"     - {instance['id']}: {instance['properties'].get('hasName', 'N/A')}")

def demo_utilisation_outils():
    """Démonstration de l'utilisation des outils"""
    print("\n\n🛠️ DÉMONSTRATION DES OUTILS")
    print("=" * 50)
    
    # Initialise la base de connaissances
    kb = KnowledgeBase()
    
    # 1. Utilisation de l'outil d'introspection
    print("\n1. Utilisation de l'outil d'introspection:")
    ontology_info = tools.introspect_ontology_tool(kb)
    
    # 2. Utilisation de l'outil d'extension
    print("\n2. Utilisation de l'outil d'extension:")
    
    # Création d'une classe "Projet"
    projet_properties = [
        {'name': 'hasName', 'type': 'string', 'label': 'Nom du projet'},
        {'name': 'hasClient', 'type': 'Client', 'label': 'Client du projet'},
        {'name': 'hasBudget', 'type': 'float', 'label': 'Budget du projet'},
        {'name': 'hasStatus', 'type': 'string', 'label': 'Statut du projet'}
    ]
    
    success, message = tools.extend_ontology_tool('Projet', projet_properties, kb)
    print(f"   {message}")
    
    # 3. Utilisation de l'outil de création d'instance
    print("\n3. Utilisation de l'outil de création d'instance:")
    
    # Trouve un client existant
    clients = kb.get_clients()
    if clients:
        client_id = clients[0]['id']
        
        projet_properties = {
            'hasName': 'Refonte site web',
            'hasClient': client_id,
            'hasBudget': 5000.0,
            'hasStatus': 'En cours'
        }
        
        success, message = tools.create_instance_tool('Projet', projet_properties, kb)
        print(f"   {message}")
    
    # 4. Utilisation de l'outil de requête
    print("\n4. Utilisation de l'outil de requête:")
    results = tools.query_ontology_tool('classes', kb)
    print(f"   Classes trouvées: {len(results)}")

if __name__ == "__main__":
    print("=== Démo Introspection ===")
    kb = KnowledgeBase()
    # Ajoute ici tes tests ou introspections spécifiques

    try:
        # Démonstration 1: Introspection
        demo_introspection()
        
        # Démonstration 2: Extension dynamique
        demo_extension_dynamique()
        
        # Démonstration 3: Utilisation des outils
        demo_utilisation_outils()
        
        print("\n\n✅ DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
        print("L'ontologie a été étendue dynamiquement sans modification du code source.")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc() 