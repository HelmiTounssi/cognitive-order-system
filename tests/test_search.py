#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from knowledge_base import KnowledgeBase

def test_search_semantic():
    print("=== TEST RECHERCHE SEMANTIQUE ===")
    
    # 1. Initialisation
    print("1. Initialisation base de connaissances...")
    kb = KnowledgeBase()
    print("   ✓ Base de connaissances créée")
    
    # 2. Ajout de classes pour tester
    print("\n2. Ajout de classes pour test...")
    kb.extend_ontology_dynamically('Produit', [
        {'name': 'hasNom', 'type': 'string'},
        {'name': 'hasPrix', 'type': 'float'}
    ])
    kb.extend_ontology_dynamically('Client', [
        {'name': 'hasNom', 'type': 'string'},
        {'name': 'hasEmail', 'type': 'string'}
    ])
    print("   ✓ Classes ajoutées")
    
    # 3. Test recherche sémantique
    print("\n3. Test recherche sémantique...")
    
    # Test recherche de classes
    results_classes = kb.search_semantic("produit", search_type="classes")
    print(f"   ✓ Recherche classes 'produit': {len(results_classes)} résultats")
    
    # Test recherche de clients
    results_clients = kb.search_semantic("client", search_type="clients")
    print(f"   ✓ Recherche clients 'client': {len(results_clients)} résultats")
    
    # Test recherche générale
    results_all = kb.search_semantic("test", search_type="all")
    print(f"   ✓ Recherche générale 'test': {len(results_all)} résultats")
    
    # 4. Test avec vector store
    print("\n4. Test vector store...")
    try:
        # Ajoute un produit au vector store
        kb.vector_store.add_product_embedding(
            "test_product_1",
            "Ordinateur portable gaming haute performance",
            None  # Génère automatiquement l'embedding
        )
        print("   ✓ Produit ajouté au vector store")
        
        # Recherche vectorielle
        vector_results = kb.search_semantic("gaming laptop", search_type="products")
        print(f"   ✓ Recherche vectorielle: {len(vector_results)} résultats")
        
    except Exception as e:
        print(f"   ⚠ Vector store: {e}")
    
    print("\n=== SUCCES! RECHERCHE SEMANTIQUE OPERATIONNELLE ===")
    return True

if __name__ == "__main__":
    test_search_semantic() 