"""
API Admin Flask - Interface d'administration du système cognitif
Endpoints pour la gestion des règles, configurations, ontologies et assistants LLM
"""

import os
import sys
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path

# Ajouter la racine du projet au PYTHONPATH pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Imports du projet
from src.core.rule_engine import AdvancedRuleEngine, BusinessRule
from src.config.config_manager import ConfigurationManager
from src.core.knowledge_base import KnowledgeBase
from src.rag.vector_store import VectorStore
from src.llm.llm_assistants import LLMAssistant
from src.rag.rag_system import HybridRAGSystem
from src.rag.rag_chat_interface import RAGChatInterface
from src.mcp import tools
from src.llm.llm_interface import LLMInterface

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin

# Instance globale du moteur de règles
rule_engine = AdvancedRuleEngine()

# Instance globale du gestionnaire de configuration
config_manager = ConfigurationManager()

# Instances globales
kb = KnowledgeBase()
vs = VectorStore()

llm_assistant = LLMAssistant()

# Instances RAG
llm_interface = LLMInterface()
rag_system = HybridRAGSystem(kb, vs, llm_interface)
rag_chat = RAGChatInterface(rag_system)


@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Récupère toutes les règles métier"""
    try:
        rules = []
        for rule in rule_engine.business_rules:
            rules.append({
                'name': rule.name,
                'description': rule.description,
                'conditions': rule.conditions,
                'actions': rule.actions,
                'priority': rule.priority,
                'category': rule.category,
                'enabled': rule.enabled,
                'created_at': rule.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'rules': rules,
            'total': len(rules)
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des règles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules', methods=['POST'])
def create_rule():
    """Crée une nouvelle règle métier"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'description', 'conditions', 'actions', 'priority', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Champ requis manquant: {field}'
                }), 400
        
        # Création de la règle
        rule = BusinessRule(
            name=data['name'],
            description=data['description'],
            conditions=data['conditions'],
            actions=data['actions'],
            priority=data['priority'],
            category=data['category'],
            enabled=data.get('enabled', True)
        )
        
        rule_engine.add_business_rule(rule)
        
        return jsonify({
            'success': True,
            'message': f'Règle "{rule.name}" créée avec succès',
            'rule': {
                'name': rule.name,
                'description': rule.description,
                'conditions': rule.conditions,
                'actions': rule.actions,
                'priority': rule.priority,
                'category': rule.category,
                'enabled': rule.enabled,
                'created_at': rule.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de la règle: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules/<rule_name>', methods=['PUT'])
def update_rule(rule_name):
    """Met à jour une règle existante"""
    try:
        data = request.get_json()
        
        # Mise à jour de la règle
        success = rule_engine.update_business_rule(rule_name, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Règle "{rule_name}" mise à jour avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Règle "{rule_name}" non trouvée'
            }), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la règle: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules/<rule_name>', methods=['DELETE'])
def delete_rule(rule_name):
    """Supprime une règle"""
    try:
        success = rule_engine.remove_business_rule(rule_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Règle "{rule_name}" supprimée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Règle "{rule_name}" non trouvée'
            }), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la règle: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules/test', methods=['POST'])
def test_rule():
    """Teste une requête avec le moteur de règles"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Requête manquante'
            }), 400
        
        # Traitement de la requête
        result = rule_engine.process_query(query)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du test de règle: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules/statistics', methods=['GET'])
def get_statistics():
    """Récupère les statistiques du moteur de règles"""
    try:
        stats = rule_engine.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules/export', methods=['GET'])
def export_rules():
    """Exporte toutes les règles au format JSON"""
    try:
        format_type = request.args.get('format', 'json')
        rules_data = rule_engine.export_rules(format_type)
        
        return jsonify({
            'success': True,
            'format': format_type,
            'data': rules_data
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export des règles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules/import', methods=['POST'])
def import_rules():
    """Importe des règles depuis un fichier JSON"""
    try:
        data = request.get_json()
        rules_data = data.get('data', '')
        format_type = data.get('format', 'json')
        
        if not rules_data:
            return jsonify({
                'success': False,
                'error': 'Données d\'import manquantes'
            }), 400
        
        rule_engine.import_rules(rules_data, format_type)
        
        return jsonify({
            'success': True,
            'message': 'Règles importées avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import des règles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules/templates', methods=['GET'])
def get_rule_templates():
    """Récupère les modèles de règles disponibles"""
    try:
        templates = rule_engine.rule_templates
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules/categories', methods=['GET'])
def get_rule_categories():
    """Récupère les catégories de règles"""
    try:
        categories = rule_engine._get_rule_categories()
        
        return jsonify({
            'success': True,
            'categories': categories
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des catégories: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Point de terminaison de santé de l'API"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Rule Engine Admin API'
    })


# --- Endpoints pour les outils simulés ---

@app.route('/api/tools/stock', methods=['POST'])
def test_stock():
    """Test de l'API de gestion de stock"""
    try:
        data = request.get_json()
        action = data.get('action', 'check_stock')
        product_id = data.get('product_id', 'TEST-001')
        
        # Simulation de la logique de stock
        if action == 'check_stock':
            result = {
                'success': True,
                'product_id': product_id,
                'available_quantity': 150,
                'reserved_quantity': 25,
                'total_quantity': 175,
                'status': 'in_stock',
                'last_updated': datetime.now().isoformat()
            }
        else:
            result = {
                'success': False,
                'error': f'Action non supportée: {action}'
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur lors du test stock: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tools/payment', methods=['POST'])
def test_payment():
    """Test de l'API de paiement"""
    try:
        data = request.get_json()
        action = data.get('action', 'process_payment')
        amount = data.get('amount', 0.0)
        
        # Simulation de la logique de paiement
        if action == 'process_payment':
            result = {
                'success': True,
                'transaction_id': f'TXN-{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'amount': amount,
                'currency': 'EUR',
                'status': 'completed',
                'payment_method': 'card',
                'timestamp': datetime.now().isoformat()
            }
        else:
            result = {
                'success': False,
                'error': f'Action non supportée: {action}'
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur lors du test paiement: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tools/delivery', methods=['POST'])
def test_delivery():
    """Test de l'API de livraison"""
    try:
        data = request.get_json()
        action = data.get('action', 'check_delivery')
        address = data.get('address', 'Paris, France')
        
        # Simulation de la logique de livraison
        if action == 'check_delivery':
            result = {
                'success': True,
                'address': address,
                'delivery_available': True,
                'estimated_delivery': '2-3 jours ouvrables',
                'shipping_cost': 8.50,
                'express_available': True,
                'express_cost': 15.00,
                'express_delivery': '24h',
                'timestamp': datetime.now().isoformat()
            }
        else:
            result = {
                'success': False,
                'error': f'Action non supportée: {action}'
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur lors du test livraison: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# --- Endpoints pour la gestion des configurations ---

@app.route('/api/configurations', methods=['GET'])
def list_configurations():
    """Liste toutes les configurations disponibles"""
    try:
        configs = config_manager.list_configurations()
        
        return jsonify({
            'success': True,
            'configurations': configs,
            'total': len(configs)
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la liste des configurations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/configurations/export', methods=['POST'])
def export_configuration():
    """Exporte la configuration complète du système"""
    try:
        data = request.get_json() or {}
        format_type = data.get('format', 'json')
        filename = data.get('filename')
        
        # Export de la configuration
        filepath = config_manager.export_configuration(
            rule_engine=rule_engine,
            knowledge_base=kb,
            vector_store=vs,
            format=format_type,
            filename=filename
        )
        
        return jsonify({
            'success': True,
            'message': 'Configuration exportée avec succès',
            'filepath': filepath,
            'filename': Path(filepath).name
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export de configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/configurations/import', methods=['POST'])
def import_configuration():
    """Importe une configuration depuis un fichier"""
    try:
        # Vérification si un fichier a été uploadé
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Aucun fichier sélectionné'
            }), 400
        
        # Sauvegarde temporaire du fichier
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            file.save(tmp_file.name)
            tmp_filepath = tmp_file.name
        
        try:
            # Import de la configuration
            config_data = config_manager.import_configuration(tmp_filepath)
            
            # Application de la configuration
            success = config_manager.apply_configuration(config_data, rule_engine, kb, vs)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Configuration importée et appliquée avec succès',
                    'config_name': config_data.get('name', 'Configuration inconnue'),
                    'version': config_data.get('version', '1.0')
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Erreur lors de l\'application de la configuration'
                }), 500
                
        finally:
            # Nettoyage du fichier temporaire
            import os
            if os.path.exists(tmp_filepath):
                os.unlink(tmp_filepath)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import de configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/configurations/<filename>', methods=['GET'])
def download_configuration(filename):
    """Télécharge une configuration spécifique"""
    try:
        filepath = config_manager.config_dir / filename
        
        if not filepath.exists():
            return jsonify({
                'success': False,
                'error': 'Fichier de configuration non trouvé'
            }), 404
        
        from flask import send_file
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/configurations/<filename>', methods=['DELETE'])
def delete_configuration(filename):
    """Supprime une configuration"""
    try:
        filepath = config_manager.config_dir / filename
        
        if not filepath.exists():
            return jsonify({
                'success': False,
                'error': 'Fichier de configuration non trouvé'
            }), 404
        
        filepath.unlink()
        
        return jsonify({
            'success': True,
            'message': f'Configuration "{filename}" supprimée avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# --- Endpoints pour la gestion de l'ontologie ---

@app.route('/api/ontology/entities', methods=['GET'])
def get_entities():
    """Récupère toutes les entités de l'ontologie"""
    try:
        # Récupération de l'ontologie complète
        ontology_data = kb.introspect_ontology()
        classes = ontology_data.get('classes', [])
        properties = ontology_data.get('properties', [])
        
        # Enrichir chaque classe avec ses propriétés
        enriched_entities = []
        for class_info in classes:
            class_name = class_info['name']
            class_uri = class_info['uri']
            
            # Récupérer les propriétés associées à cette classe
            class_properties = []
            for prop_info in properties:
                prop_uri = prop_info['uri']
                # Vérifier si la propriété est associée à cette classe
                # (simplification: on prend toutes les propriétés pour l'instant)
                class_properties.append(prop_info['name'])
            
            # Créer l'entité enrichie
            enriched_entity = {
                'name': class_name,
                'uri': class_uri,
                'label': class_info.get('label', class_name),
                'properties': class_properties,
                'instances_count': class_info.get('instances_count', 0),
                'description': f"Classe {class_name} avec {len(class_properties)} propriétés"
            }
            enriched_entities.append(enriched_entity)
        
        return jsonify({
            'success': True,
            'entities': enriched_entities,
            'total': len(enriched_entities)
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des entités: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ontology/entities', methods=['POST'])
def create_entity():
    """Crée une nouvelle entité dans l'ontologie"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        if 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Nom de l\'entité requis'
            }), 400
        
        # Création de l'entité
        entity_name = data['name']
        properties = data.get('properties', [])
        description = data.get('description', '')
        
        # Extension dynamique de l'ontologie
        success = kb.extend_ontology_dynamically(entity_name, properties)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Entité "{entity_name}" créée avec succès',
                'entity': {
                    'name': entity_name,
                    'properties': properties,
                    'description': description,
                    'uri': f'http://example.com/ontology#{entity_name}'
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erreur lors de la création de l\'entité "{entity_name}"'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'entité: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ontology/entities/<entity_name>', methods=['PUT'])
def update_entity(entity_name):
    """Met à jour une entité existante"""
    try:
        data = request.get_json()
        
        # Mise à jour de l'entité
        properties = data.get('properties', [])
        description = data.get('description', '')
        
        # Suppression de l'ancienne entité et création de la nouvelle
        success = kb.extend_ontology_dynamically(entity_name, properties)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Entité "{entity_name}" mise à jour avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erreur lors de la mise à jour de l\'entité "{entity_name}"'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'entité: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ontology/entities/<entity_name>', methods=['DELETE'])
def delete_entity(entity_name):
    """Supprime une entité de l'ontologie"""
    try:
        # Suppression de l'entité (simulation)
        # Note: Dans une vraie implémentation, il faudrait gérer la suppression dans rdflib
        success = True  # Simulation
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Entité "{entity_name}" supprimée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Erreur lors de la suppression de l\'entité "{entity_name}"'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'entité: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ontology/export', methods=['GET'])
def export_ontology():
    """Exporte l'ontologie complète"""
    try:
        # Récupération de l'ontologie
        ontology_data = kb.introspect_ontology()
        
        return jsonify({
            'success': True,
            'ontology': ontology_data
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export de l'ontologie: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ontology/import', methods=['POST'])
def import_ontology():
    """Importe une ontologie depuis un fichier"""
    try:
        # Vérification si un fichier a été uploadé
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Aucun fichier sélectionné'
            }), 400
        
        # Import de l'ontologie (simulation)
        success = True  # Simulation
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Ontologie importée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'import de l\'ontologie'
            }), 500
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import de l'ontologie: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/generate_workflow', methods=['POST'])
def generate_workflow():
    """Génère un workflow automatiquement avec l'assistant LLM"""
    try:
        data = request.get_json()
        domain = data.get('domain', '')
        business_context = data.get('business_context', '')
        
        if not domain or not business_context:
            return jsonify({
                'success': False,
                'error': 'Domaine et contexte métier requis'
            }), 400
        
        # Génération du workflow
        workflow = llm_assistant.generate_workflow(domain, business_context)
        
        return jsonify({
            'success': True,
            'workflow': workflow
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du workflow: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/generate_patterns', methods=['POST'])
def generate_patterns():
    """Génère des patterns d'extraction automatiquement"""
    try:
        data = request.get_json()
        entity_type = data.get('entity_type', '')
        sample_data = data.get('sample_data', '')
        
        if not entity_type or not sample_data:
            return jsonify({
                'success': False,
                'error': 'Type d\'entité et données d\'exemple requis'
            }), 400
        
        # Génération des patterns
        patterns = llm_assistant.generate_extraction_patterns(entity_type, sample_data)
        
        return jsonify({
            'success': True,
            'patterns': patterns
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des patterns: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/generate_rules', methods=['POST'])
def generate_rules():
    """Génère des règles métier automatiquement"""
    try:
        data = request.get_json()
        business_scenario = data.get('business_scenario', '')
        constraints = data.get('constraints', [])
        
        if not business_scenario:
            return jsonify({
                'success': False,
                'error': 'Scénario métier requis'
            }), 400
        
        # Génération des règles
        rules = llm_assistant.generate_business_rules(business_scenario, constraints)
        
        return jsonify({
            'success': True,
            'rules': rules
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des règles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/assistants/status', methods=['GET'])
def get_assistants_status():
    """Récupère le statut des assistants LLM"""
    try:
        status = {
            'workflow_generator': llm_assistant.workflow_generator.is_available(),
            'pattern_generator': llm_assistant.pattern_generator.is_available(),
            'rule_generator': llm_assistant.rule_generator.is_available()
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/assistants/configure', methods=['POST'])
def configure_assistants():
    """Configure les assistants LLM"""
    try:
        data = request.get_json()
        
        # Configuration des assistants
        llm_assistant.configure(
            api_key=data.get('api_key'),
            model=data.get('model', 'gpt-4'),
            temperature=data.get('temperature', 0.7)
        )
        
        return jsonify({
            'success': True,
            'message': 'Assistants LLM configurés avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/assistants/templates', methods=['GET'])
def get_assistant_templates():
    """Récupère les templates disponibles pour les assistants"""
    try:
        templates = {
            'workflow_templates': llm_assistant.workflow_generator.get_templates(),
            'pattern_templates': llm_assistant.pattern_generator.get_templates(),
            'rule_templates': llm_assistant.rule_generator.get_templates()
        }
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des templates: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/assistants/validate', methods=['POST'])
def validate_assistant_output():
    """Valide la sortie d'un assistant LLM"""
    try:
        data = request.get_json()
        output_type = data.get('output_type', '')
        content = data.get('content', '')
        
        if not output_type or not content:
            return jsonify({
                'success': False,
                'error': 'Type de sortie et contenu requis'
            }), 400
        
        # Validation selon le type
        if output_type == 'workflow':
            validation = llm_assistant.workflow_generator.validate_output(content)
        elif output_type == 'patterns':
            validation = llm_assistant.pattern_generator.validate_output(content)
        elif output_type == 'rules':
            validation = llm_assistant.rule_generator.validate_output(content)
        else:
            return jsonify({
                'success': False,
                'error': 'Type de sortie invalide'
            }), 400
        
        return jsonify({
            'success': True,
            'validation': validation
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la validation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/save_workflow', methods=['POST'])
def save_workflow():
    """Sauvegarde un workflow généré dans la base de connaissances"""
    try:
        data = request.get_json()
        workflow_data = data.get('workflow', {})
        metadata = data.get('metadata', {})
        
        if not workflow_data:
            return jsonify({
                'success': False,
                'error': 'Données de workflow manquantes'
            }), 400
        
        # Créer une entité workflow dans la base de connaissances
        workflow_entity = {
            'type': 'workflow',
            'name': metadata.get('name', f'workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
            'domain': metadata.get('domain', 'generic'),
            'description': metadata.get('description', 'Workflow généré par assistant LLM'),
            'steps': workflow_data,
            'created_at': datetime.now().isoformat(),
            'source': 'llm_assistant'
        }
        
        # Ajouter à la base de connaissances
        kb.add_entity(workflow_entity['name'], workflow_entity)
        
        return jsonify({
            'success': True,
            'message': f'Workflow "{workflow_entity["name"]}" sauvegardé avec succès',
            'workflow_id': workflow_entity['name']
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du workflow: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/save_patterns', methods=['POST'])
def save_patterns():
    """Sauvegarde des patterns générés dans la base de connaissances"""
    try:
        data = request.get_json()
        patterns_data = data.get('patterns', [])
        metadata = data.get('metadata', {})
        
        if not patterns_data:
            return jsonify({
                'success': False,
                'error': 'Données de patterns manquantes'
            }), 400
        
        # Créer une entité patterns dans la base de connaissances
        patterns_entity = {
            'type': 'extraction_patterns',
            'name': metadata.get('name', f'patterns_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
            'entity_type': metadata.get('entity_type', 'generic'),
            'description': metadata.get('description', 'Patterns d\'extraction générés par assistant LLM'),
            'patterns': patterns_data,
            'created_at': datetime.now().isoformat(),
            'source': 'llm_assistant'
        }
        
        # Ajouter à la base de connaissances
        kb.add_entity(patterns_entity['name'], patterns_entity)
        
        return jsonify({
            'success': True,
            'message': f'Patterns "{patterns_entity["name"]}" sauvegardés avec succès',
            'patterns_id': patterns_entity['name']
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des patterns: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/save_rules', methods=['POST'])
def save_rules():
    """Sauvegarde des règles générées dans la base de connaissances"""
    try:
        data = request.get_json()
        rules_data = data.get('rules', [])
        metadata = data.get('metadata', {})
        
        if not rules_data:
            return jsonify({
                'success': False,
                'error': 'Données de règles manquantes'
            }), 400
        
        # Créer une entité rules dans la base de connaissances
        rules_entity = {
            'type': 'business_rules',
            'name': metadata.get('name', f'rules_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
            'domain': metadata.get('domain', 'generic'),
            'description': metadata.get('description', 'Règles métier générées par assistant LLM'),
            'rules': rules_data,
            'created_at': datetime.now().isoformat(),
            'source': 'llm_assistant'
        }
        
        # Ajouter à la base de connaissances
        kb.add_entity(rules_entity['name'], rules_entity)
        
        return jsonify({
            'success': True,
            'message': f'Règles "{rules_entity["name"]}" sauvegardées avec succès',
            'rules_id': rules_entity['name']
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des règles: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/saved_items', methods=['GET'])
def get_saved_items():
    """Récupère tous les éléments sauvegardés par les assistants LLM"""
    try:
        # Récupérer tous les éléments de la base de connaissances
        all_entities = kb.get_all_entities()
        
        # Filtrer ceux générés par les assistants LLM
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
        
        return jsonify({
            'success': True,
            'items': llm_items,
            'total': len(llm_items['workflows']) + len(llm_items['patterns']) + len(llm_items['rules'])
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des éléments sauvegardés: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/apply_workflow/<workflow_id>', methods=['POST'])
def apply_workflow(workflow_id):
    """Applique un workflow sauvegardé"""
    try:
        data = request.get_json()
        input_data = data.get('input_data', {})
        
        # Récupérer le workflow depuis la base de connaissances
        workflow_entity = kb.get_entity(workflow_id)
        
        if not workflow_entity or workflow_entity.get('type') != 'workflow':
            return jsonify({
                'success': False,
                'error': f'Workflow "{workflow_id}" non trouvé'
            }), 404
        
        # Simuler l'exécution du workflow
        steps = workflow_entity.get('steps', [])
        results = []
        
        for step in steps:
            step_result = {
                'step': step.get('step', 0),
                'action': step.get('action', ''),
                'status': 'executed',
                'result': f'Action {step.get("action")} exécutée avec succès'
            }
            results.append(step_result)
        
        return jsonify({
            'success': True,
            'workflow_name': workflow_entity.get('name'),
            'execution_results': results,
            'message': f'Workflow "{workflow_entity.get("name")}" appliqué avec succès'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'application du workflow: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# --- Endpoints RAG (Retrieval-Augmented Generation) ---

@app.route('/api/rag/chat', methods=['POST'])
def rag_chat_endpoint():
    """Endpoint principal pour le chat RAG"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message manquant'
            }), 400
        
        # Envoyer le message et obtenir la réponse
        response_message = rag_chat.send_message(message, conversation_id)
        
        # Récupérer la conversation mise à jour
        conversation = rag_chat.get_conversation(response_message.id.split('_')[0])
        
        return jsonify({
            'success': True,
            'response': {
                'id': response_message.id,
                'content': response_message.content,
                'timestamp': response_message.timestamp.isoformat(),
                'metadata': response_message.metadata,
                'rag_context': response_message.rag_context
            },
            'conversation_id': conversation.id if conversation else None,
            'conversation_title': conversation.title if conversation else None
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du chat RAG: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/conversations', methods=['GET'])
def get_conversations():
    """Récupère toutes les conversations"""
    try:
        conversations = rag_chat.get_all_conversations()
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des conversations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/conversations', methods=['POST'])
def create_conversation():
    """Crée une nouvelle conversation"""
    try:
        data = request.get_json()
        initial_query = data.get('initial_query')
        
        conversation_id = rag_chat.start_new_conversation(initial_query)
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la création de conversation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Récupère une conversation spécifique"""
    try:
        conversation = rag_chat.get_conversation(conversation_id)
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Conversation non trouvée'
            }), 404
        
        # Convertir les messages pour la sérialisation JSON
        messages = []
        for msg in conversation.messages:
            messages.append({
                'id': msg.id,
                'content': msg.content,
                'sender': msg.sender,
                'timestamp': msg.timestamp.isoformat(),
                'metadata': msg.metadata,
                'rag_context': msg.rag_context
            })
        
        return jsonify({
            'success': True,
            'conversation': {
                'id': conversation.id,
                'title': conversation.title,
                'messages': messages,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'domain': conversation.domain,
                'summary': conversation.summary
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de conversation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Supprime une conversation"""
    try:
        success = rag_chat.delete_conversation(conversation_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Conversation supprimée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Conversation non trouvée'
            }), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de conversation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/conversations/<conversation_id>/export', methods=['GET'])
def export_conversation(conversation_id):
    """Exporte une conversation au format JSON"""
    try:
        conversation_data = rag_chat.export_conversation(conversation_id)
        
        if not conversation_data:
            return jsonify({
                'success': False,
                'error': 'Conversation non trouvée'
            }), 404
        
        return jsonify({
            'success': True,
            'conversation': conversation_data
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export de conversation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/conversations/import', methods=['POST'])
def import_conversation():
    """Importe une conversation depuis un fichier JSON"""
    try:
        data = request.get_json()
        conversation_data = data.get('conversation', {})
        
        if not conversation_data:
            return jsonify({
                'success': False,
                'error': 'Données de conversation manquantes'
            }), 400
        
        conversation_id = rag_chat.import_conversation(conversation_data)
        
        if conversation_id:
            return jsonify({
                'success': True,
                'conversation_id': conversation_id,
                'message': 'Conversation importée avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'import'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de l'import de conversation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/conversations/<conversation_id>/suggestions', methods=['GET'])
def get_suggestions(conversation_id):
    """Récupère des suggestions de questions pour une conversation"""
    try:
        suggestions = rag_chat.get_suggestions(conversation_id)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des suggestions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/conversations/<conversation_id>/analytics', methods=['GET'])
def get_conversation_analytics(conversation_id):
    """Récupère les analytics d'une conversation"""
    try:
        analytics = rag_chat.get_conversation_analytics(conversation_id)
        
        return jsonify({
            'success': True,
            'analytics': analytics
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/search', methods=['POST'])
def hybrid_search():
    """Recherche hybride (vector + graph)"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Requête manquante'
            }), 400
        
        # Effectuer la recherche hybride
        vector_results, graph_results = rag_system.search_hybrid(query, top_k)
        
        return jsonify({
            'success': True,
            'query': query,
            'vector_results': vector_results,
            'graph_results': graph_results,
            'total_results': len(vector_results) + len(graph_results)
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche hybride: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/context', methods=['POST'])
def get_business_context():
    """Récupère le contexte métier pour une requête donnée"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Requête manquante'
            }), 400
        
        context = rag_system.get_business_context(query)
        
        return jsonify({
            'success': True,
            'context': context
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du contexte: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/status', methods=['GET'])
def get_rag_status():
    """Vérifie le statut du système RAG"""
    try:
        # Vérifier que tous les composants RAG sont disponibles
        status_checks = {
            'knowledge_base': kb is not None,
            'vector_store': vs is not None,
            'llm_interface': llm_interface is not None,
            'rag_system': rag_system is not None,
            'rag_chat': rag_chat is not None
        }
        
        # Vérifier que les composants principaux fonctionnent
        all_online = all(status_checks.values())
        
        # Test de connectivité LLM (optionnel)
        llm_working = False
        try:
            # Test simple avec l'LLM
            test_response = llm_interface.generate_response("Test de connectivité", max_tokens=10)
            llm_working = len(test_response) > 0
        except Exception as e:
            logger.warning(f"LLM non disponible: {e}")
        
        return jsonify({
            'success': True,
            'status': 'online' if all_online else 'offline',
            'components': status_checks,
            'llm_working': llm_working,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du statut RAG: {e}")
        return jsonify({
            'success': False,
            'status': 'offline',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Récupère le statut global du système"""
    try:
        # Vérifier le statut des composants
        components_status = {
            'rule_engine': {
                'status': 'online' if rule_engine else 'offline',
                'rules_count': len(rule_engine.business_rules) if rule_engine else 0,
                'last_update': datetime.now().isoformat()
            },
            'knowledge_base': {
                'status': 'online' if kb else 'offline',
                'entities_count': len(kb.entities) if kb else 0,
                'last_update': datetime.now().isoformat()
            },
            'vector_store': {
                'status': 'online' if vs else 'offline',
                'documents_count': vs.get_document_count() if vs else 0,
                'last_update': datetime.now().isoformat()
            },
            'llm_interface': {
                'status': 'online' if llm_interface else 'offline',
                'providers': ['openai'] if llm_interface else [],
                'last_update': datetime.now().isoformat()
            },
            'rag_system': {
                'status': 'online' if rag_system else 'offline',
                'conversations_count': len(rag_chat.conversations) if rag_chat else 0,
                'last_update': datetime.now().isoformat()
            },
            'config_manager': {
                'status': 'online' if config_manager else 'offline',
                'configs_count': len(config_manager.configurations) if config_manager else 0,
                'last_update': datetime.now().isoformat()
            }
        }
        
        # Calculer le statut global
        online_components = sum(1 for comp in components_status.values() if comp['status'] == 'online')
        total_components = len(components_status)
        health_percentage = (online_components / total_components) * 100 if total_components > 0 else 0
        
        if health_percentage >= 90:
            global_status = 'excellent'
        elif health_percentage >= 70:
            global_status = 'good'
        elif health_percentage >= 50:
            global_status = 'warning'
        else:
            global_status = 'critical'
        
        # Informations système
        system_info = {
            'platform': 'Windows',
            'python_version': '3.9+',
            'cpu_count': 4,
            'memory_total': 8192,
            'memory_available': 6144,
            'memory_percent': 25,
            'disk_usage': 45
        }
        
        # Générer des recommandations
        recommendations = _get_system_recommendations(components_status, system_info)
        
        return jsonify({
            'success': True,
            'system_status': {
                'global_status': global_status,
                'health_percentage': health_percentage,
                'online_components': online_components,
                'total_components': total_components,
                'timestamp': datetime.now().isoformat()
            },
            'system_info': system_info,
            'components': components_status,
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut système: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/mcp/status', methods=['GET'])
def get_mcp_status():
    """Récupère le statut du serveur MCP"""
    try:
        import socket
        
        # Vérifier si le serveur MCP est accessible sur le port 8002
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Timeout de 2 secondes
        
        result = sock.connect_ex(('localhost', 8002))
        sock.close()
        
        if result == 0:
            return jsonify({
                'success': True,
                'status': 'connected',
                'message': 'Serveur MCP connecté sur ws://localhost:8002',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': True,
                'status': 'disconnected',
                'message': 'Serveur MCP non accessible sur le port 8002',
                'timestamp': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du statut MCP: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def _get_system_recommendations(components_status, system_info):
    """Génère des recommandations basées sur le statut du système"""
    recommendations = []
    
    # Vérifications système
    if system_info['memory_percent'] > 80:
        recommendations.append("⚠️ Utilisation mémoire élevée - Considérez redémarrer l'application")
    
    if system_info['disk_usage'] > 90:
        recommendations.append("⚠️ Espace disque faible - Libérez de l'espace")
    
    # Vérifications composants
    if components_status['llm_interface']['status'] == 'offline':
        recommendations.append("🔧 LLM Interface hors ligne - Vérifiez la clé API OpenAI")
    
    if components_status['knowledge_base']['entities_count'] == 0:
        recommendations.append("📝 Base de connaissances vide - Importez des entités")
    
    if components_status['rule_engine']['rules_count'] == 0:
        recommendations.append("⚙️ Aucune règle métier - Créez ou importez des règles")
    
    if components_status['vector_store']['documents_count'] == 0:
        recommendations.append("🔍 Base vectorielle vide - Ajoutez des embeddings")
    
    if not recommendations:
        recommendations.append("✅ Système opérationnel - Tous les composants fonctionnent correctement")
    
    return recommendations


if __name__ == '__main__':
    print("🚀 Démarrage de l'API d'administration du moteur de règles...")
    print("📊 Endpoints disponibles:")
    print("  - GET  /api/rules - Liste des règles")
    print("  - POST /api/rules - Créer une règle")
    print("  - PUT  /api/rules/<name> - Modifier une règle")
    print("  - DELETE /api/rules/<name> - Supprimer une règle")
    print("  - POST /api/rules/test - Tester une requête")
    print("  - GET  /api/rules/statistics - Statistiques")
    print("  - GET  /api/rules/export - Exporter les règles")
    print("  - POST /api/rules/import - Importer des règles")
    print("  - GET  /api/rules/templates - Modèles de règles")
    print("  - GET  /api/rules/categories - Catégories")
    print("  - GET  /api/health - Santé de l'API")
    print("  - GET  /api/configurations - Liste des configurations")
    print("  - POST /api/configurations/export - Exporter une configuration")
    print("  - POST /api/configurations/import - Importer une configuration")
    print("  - GET  /api/configurations/<filename> - Télécharger une configuration")
    print("  - DELETE /api/configurations/<filename> - Supprimer une configuration")
    print("  - GET  /api/ontology/entities - Récupérer toutes les entités de l'ontologie")
    print("  - POST /api/ontology/entities - Créer une nouvelle entité dans l'ontologie")
    print("  - PUT  /api/ontology/entities/<entity_name> - Mettre à jour une entité existante")
    print("  - DELETE /api/ontology/entities/<entity_name> - Supprimer une entité de l'ontologie")
    print("  - GET  /api/ontology/export - Exporter l'ontologie complète")
    print("  - POST /api/ontology/import - Importer une ontologie depuis un fichier")
    print("  - POST /api/llm/generate_workflow - Générer un workflow")
    print("  - POST /api/llm/generate_patterns - Générer des patterns")
    print("  - POST /api/llm/generate_rules - Générer des règles")
    print("  - GET  /api/llm/assistants/status - Récupérer le statut des assistants LLM")
    print("  - POST /api/llm/assistants/configure - Configurer les assistants LLM")
    print("  - GET  /api/llm/assistants/templates - Récupérer les templates disponibles pour les assistants")
    print("  - POST /api/llm/assistants/validate - Valider la sortie d'un assistant LLM")
    print("  - POST /api/llm/save_workflow - Sauvegarder un workflow")
    print("  - POST /api/llm/save_patterns - Sauvegarder des patterns")
    print("  - POST /api/llm/save_rules - Sauvegarder des règles")
    print("  - GET  /api/llm/saved_items - Récupérer tous les éléments sauvegardés")
    print("  - POST /api/llm/apply_workflow/<workflow_id> - Appliquer un workflow")
    print("  - POST /api/rag/chat - Chat RAG")
    print("  - GET  /api/rag/conversations - Liste des conversations")
    print("  - POST /api/rag/conversations - Créer une nouvelle conversation")
    print("  - GET  /api/rag/conversations/<conversation_id> - Récupérer une conversation")
    print("  - DELETE /api/rag/conversations/<conversation_id> - Supprimer une conversation")
    print("  - GET  /api/rag/conversations/<conversation_id>/export - Exporter une conversation")
    print("  - POST /api/rag/conversations/import - Importer une conversation")
    print("  - GET  /api/rag/conversations/<conversation_id>/suggestions - Récupérer des suggestions")
    print("  - GET  /api/rag/conversations/<conversation_id>/analytics - Récupérer les analytics")
    print("  - POST /api/rag/search - Recherche hybride")
    print("  - POST /api/rag/context - Récupérer le contexte métier")
    print("  - GET  /api/rag/status - Vérifier le statut du système RAG")
    print("  - GET  /api/system/status - Vérifier le statut global du système")
    print("  - GET  /api/mcp/status - Récupérer le statut du serveur MCP")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 