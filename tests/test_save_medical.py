#!/usr/bin/env python3
"""
Test de sauvegarde de l'exemple médical
Vérifie que l'exemple médical peut être sauvegardé et appliqué
"""

import sys
import os
import json
import yaml
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import des modules du système
from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore
from src.llm_assistants import LLMAssistant

def test_save_medical():
    """Test de sauvegarde du workflow médical"""
    print("🏥 Test de sauvegarde du workflow médical...")
    
    try:
        # Initialiser les composants
        kb = KnowledgeBase()
        llm_assistant = LLMAssistant()
        
        # Générer un workflow médical
        workflow_data = [
            {
                "step": 1,
                "action": "Vérifier les antécédents médicaux",
                "description": "Consulter l'historique médical du patient",
                "tools": ["database_query", "medical_records_api"],
                "output": "antécédents_médicaux"
            },
            {
                "step": 2,
                "action": "Analyser les symptômes",
                "description": "Évaluer les symptômes actuels du patient",
                "tools": ["symptom_analyzer", "ai_diagnosis"],
                "output": "diagnostic_préliminaire"
            },
            {
                "step": 3,
                "action": "Prescrire un traitement",
                "description": "Établir un plan de traitement personnalisé",
                "tools": ["treatment_planner", "drug_interaction_checker"],
                "output": "ordonnance_médicale"
            }
        ]
        
        # Créer une entité workflow
        workflow_entity = {
            'type': 'workflow',
            'name': f'workflow_medical_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'domain': 'healthcare',
            'description': 'Workflow de diagnostic médical généré par assistant LLM',
            'steps': workflow_data,
            'created_at': datetime.now().isoformat(),
            'source': 'llm_assistant'
        }
        
        # Sauvegarder le workflow
        success = kb.add_entity(workflow_entity['name'], workflow_entity)
        
        if success:
            print("✅ Workflow médical sauvegardé avec succès")
        else:
            print("❌ Erreur lors de la sauvegarde du workflow")
            return False
        
        # Générer des patterns médicaux
        patterns_data = [
            {
                "pattern_name": "symptom_extraction",
                "regex": r"douleur\s+(?:à|dans)\s+(\w+)",
                "description": "Extrait la localisation de la douleur"
            },
            {
                "pattern_name": "medication_extraction", 
                "regex": r"(?:prend|prendre)\s+(\w+)\s+(?:mg|g)",
                "description": "Extrait les médicaments et dosages"
            }
        ]
        
        patterns_entity = {
            'type': 'extraction_patterns',
            'name': f'patterns_medical_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'entity_type': 'healthcare',
            'description': 'Patterns d\'extraction médicale générés par assistant LLM',
            'patterns': patterns_data,
            'created_at': datetime.now().isoformat(),
            'source': 'llm_assistant'
        }
        
        success = kb.add_entity(patterns_entity['name'], patterns_entity)
        
        if success:
            print("✅ Patterns médicaux sauvegardés avec succès")
        else:
            print("❌ Erreur lors de la sauvegarde des patterns")
            return False
        
        # Générer des règles médicales
        rules_data = [
            {
                "rule_name": "contre_indication_medicament",
                "condition": "patient.allergie_medicament == true",
                "action": "alerter_medecin",
                "priority": "high"
            },
            {
                "rule_name": "dosage_adaptation",
                "condition": "patient.age > 65",
                "action": "reduire_dosage_30_percent",
                "priority": "medium"
            }
        ]
        
        rules_entity = {
            'type': 'business_rules',
            'name': f'rules_medical_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'domain': 'healthcare',
            'description': 'Règles métier médicales générées par assistant LLM',
            'rules': rules_data,
            'created_at': datetime.now().isoformat(),
            'source': 'llm_assistant'
        }
        
        success = kb.add_entity(rules_entity['name'], rules_entity)
        
        if success:
            print("✅ Règles médicales sauvegardées avec succès")
        else:
            print("❌ Erreur lors de la sauvegarde des règles")
            return False
        
        # Récupérer tous les éléments sauvegardés
        print("\n📝 Test de récupération des éléments sauvegardés...")
        all_entities = kb.get_all_entities()
        
        llm_items = {
            'workflows': [],
            'patterns': [],
            'rules': []
        }
        
        for entity_name, entity_data in all_entities.items():
            if entity_data.get('source') == 'llm_assistant':
                item_info = {
                    'id': entity_name,
                    'name': entity_data.get('name', entity_name),
                    'type': entity_data.get('type'),
                    'description': entity_data.get('description', ''),
                    'created_at': entity_data.get('created_at', ''),
                    'domain': entity_data.get('domain', 'generic')
                }
                
                if entity_data.get('type') == 'workflow':
                    llm_items['workflows'].append(item_info)
                elif entity_data.get('type') == 'extraction_patterns':
                    llm_items['patterns'].append(item_info)
                elif entity_data.get('type') == 'business_rules':
                    llm_items['rules'].append(item_info)
        
        print(f"✅ Éléments récupérés:")
        print(f"   - Workflows: {len(llm_items['workflows'])}")
        print(f"   - Patterns: {len(llm_items['patterns'])}")
        print(f"   - Règles: {len(llm_items['rules'])}")
        
        # Test de récupération d'une entité spécifique
        workflow_id = workflow_entity['name']
        retrieved_workflow = kb.get_entity(workflow_id)
        
        if retrieved_workflow:
            print(f"✅ Workflow récupéré: {retrieved_workflow.get('name')}")
        else:
            print(f"❌ Erreur lors de la récupération du workflow {workflow_id}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Test de sauvegarde des éléments médicaux")
    print("=" * 60)
    
    success = test_save_medical()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Tests de sauvegarde terminés avec succès")
    else:
        print("❌ Tests de sauvegarde échoués")
    print("=" * 60)
    
    print("\n💡 Résultats:")
    print("   - Les workflows, patterns et règles sont sauvegardés dans la base de connaissances")
    print("   - Ils peuvent être réutilisés et appliqués")
    print("   - Consultez l'onglet 'Éléments Sauvegardés' dans l'interface web") 