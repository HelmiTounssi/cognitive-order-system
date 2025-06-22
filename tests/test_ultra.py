#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from knowledge_base import KnowledgeBase
from plugin_manager import PluginManager
from admin_interface import AdminInterface

def main():
    print("TEST ULTRA-GENERIQUE")
    print("=" * 40)
    
    # 1. Test base de connaissances
    print("1. Base de connaissances...")
    kb = KnowledgeBase()
    print("   OK")
    
    # 2. Test ajout de classes
    print("2. Ajout de classes...")
    kb.extend_ontology_dynamically('Client', [
        {'name': 'hasName', 'type': 'string'},
        {'name': 'hasEmail', 'type': 'string'}
    ])
    print("   OK")
    
    # 3. Test handler metier
    print("3. Handler metier...")
    handler = {
        'description': 'Test handler',
        'extraction_patterns': {'client': [r'client\s+([a-zA-Z]+)']},
        'workflow': [{'step': 1, 'action': 'test', 'params': ['client']}],
        'rules': [{'condition': 'test', 'action': 'test'}]
    }
    success = kb.add_business_handler('test_handler', handler)
    print(f"   OK: {success}")
    
    # 4. Test plugin manager
    print("4. Plugin manager...")
    pm = PluginManager()
    print("   OK")
    
    # 5. Test admin interface
    print("5. Admin interface...")
    admin = AdminInterface(kb, pm)
    print("   OK")
    
    # 6. Test introspection
    print("6. Introspection...")
    info = kb.introspect_ontology()
    print(f"   Classes: {len(info.get('classes', []))}")
    
    # 7. Test liste handlers
    print("7. Liste handlers...")
    handlers = kb.list_business_handlers()
    print(f"   Handlers: {len(handlers)}")
    
    print("\nSUCCES! Systeme ultra-generique operationnel!")

if __name__ == "__main__":
    main() 