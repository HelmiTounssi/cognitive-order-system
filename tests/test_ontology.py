#!/usr/bin/env python3
"""
Test de gestion d'ontologie
Vérifie que la gestion d'ontologie fonctionne correctement
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5001"

def test_create_entity():
    """Test de création d'une entité"""
    print("🧪 Test de création d'entité...")
    
    entity_data = {
        "name": "Product",
        "description": "Entité représentant un produit dans le système",
        "properties": ["name", "price", "stock", "category", "description"]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/ontology/entities",
            json=entity_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Entité créée: {result['entity']['name']}")
            print(f"   Propriétés: {result['entity']['properties']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_get_entities():
    """Test de récupération des entités"""
    print("\n📋 Test de récupération des entités...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/ontology/entities")
        
        if response.status_code == 200:
            result = response.json()
            entities = result.get('entities', [])
            print(f"✅ Entités trouvées: {len(entities)}")
            
            for entity in entities:
                print(f"   📄 {entity['name']}")
                print(f"      Propriétés: {entity.get('properties', [])}")
                print(f"      Description: {entity.get('description', 'Aucune')}")
                print()
            
            return entities
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return []

def test_update_entity():
    """Test de mise à jour d'une entité"""
    print("🔄 Test de mise à jour d'entité...")
    
    update_data = {
        "name": "Product",
        "description": "Entité produit mise à jour avec nouvelles propriétés",
        "properties": ["name", "price", "stock", "category", "description", "brand", "sku"]
    }
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/ontology/entities/Product",
            json=update_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Entité mise à jour: {result['message']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_create_multiple_entities():
    """Test de création de plusieurs entités"""
    print("\n🏭 Test de création de plusieurs entités...")
    
    entities = [
        {
            "name": "Order",
            "description": "Entité représentant une commande",
            "properties": ["order_id", "customer_id", "items", "total", "status", "created_at"]
        },
        {
            "name": "Customer",
            "description": "Entité représentant un client",
            "properties": ["customer_id", "name", "email", "phone", "address"]
        },
        {
            "name": "Category",
            "description": "Entité représentant une catégorie de produits",
            "properties": ["category_id", "name", "description", "parent_category"]
        }
    ]
    
    success_count = 0
    
    for entity_data in entities:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/ontology/entities",
                json=entity_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {entity_data['name']}: {result['message']}")
                success_count += 1
            else:
                print(f"❌ {entity_data['name']}: Erreur {response.status_code}")
                
        except Exception as e:
            print(f"❌ {entity_data['name']}: Erreur de connexion - {e}")
    
    print(f"📊 Entités créées avec succès: {success_count}/{len(entities)}")
    return success_count == len(entities)

def test_export_ontology():
    """Test d'export de l'ontologie"""
    print("\n📤 Test d'export de l'ontologie...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/ontology/export")
        
        if response.status_code == 200:
            result = response.json()
            ontology = result.get('ontology', {})
            
            print(f"✅ Ontologie exportée")
            print(f"   Classes: {len(ontology.get('classes', []))}")
            print(f"   Propriétés: {len(ontology.get('properties', []))}")
            
            # Sauvegarde dans un fichier
            with open('ontology_export.json', 'w', encoding='utf-8') as f:
                json.dump(ontology, f, indent=2, ensure_ascii=False)
            
            print(f"   📄 Sauvegardé dans: ontology_export.json")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_delete_entity():
    """Test de suppression d'une entité"""
    print("\n🗑️ Test de suppression d'entité...")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/api/ontology/entities/Category")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Entité supprimée: {result['message']}")
            return True
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def main():
    """Fonction principale de test"""
    
    print("🧪 Test de la Gestion d'Ontologie")
    print("=" * 50)
    
    # Vérification que l'API est accessible
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code != 200:
            print("❌ L'API n'est pas accessible. Assurez-vous que admin_api.py est démarré.")
            return
        print("✅ API accessible")
    except Exception as e:
        print(f"❌ Impossible de se connecter à l'API: {e}")
        print("   Démarrez l'API avec: python admin_api.py")
        return
    
    # Tests
    test_create_entity()
    test_get_entities()
    test_update_entity()
    test_create_multiple_entities()
    test_export_ontology()
    test_delete_entity()
    
    # Test final
    print("\n📋 État final des entités:")
    final_entities = test_get_entities()
    
    print("\n🎉 Tests terminés!")
    print("\n🌐 Vous pouvez maintenant tester l'interface web:")
    print("   1. Allez sur l'onglet 'Base de Connaissances'")
    print("   2. Testez la création, modification et suppression d'entités")
    print("   3. Vérifiez l'export de l'ontologie")

if __name__ == "__main__":
    main() 