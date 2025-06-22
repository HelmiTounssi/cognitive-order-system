"""
Gestionnaire de Configuration Métier
Import/Export de configurations en YAML et JSON
"""

import json
import logging
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BusinessConfig:
    """Configuration métier complète du système"""
    name: str
    description: str
    version: str
    created_at: str
    updated_at: str
    
    # Configuration du moteur de règles
    rule_engine: Dict[str, Any]
    
    # Configuration de la base de connaissances
    knowledge_base: Dict[str, Any]
    
    # Configuration du vector store
    vector_store: Dict[str, Any]
    
    # Configuration LLM
    llm_config: Dict[str, Any]
    
    # Configuration des outils
    tools_config: Dict[str, Any]
    
    # Configuration de l'agent
    agent_config: Dict[str, Any]
    
    # Métadonnées
    metadata: Dict[str, Any]


class ConfigurationManager:
    """Gestionnaire de configuration pour import/export"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def export_configuration(
        self,
        rule_engine,
        knowledge_base,
        vector_store,
        llm_config: Dict = None,
        tools_config: Dict = None,
        agent_config: Dict = None,
        format: str = 'json',
        filename: str = None
    ) -> str:
        """
        Exporte la configuration complète du système
        
        Args:
            rule_engine: Instance du moteur de règles
            knowledge_base: Instance de la base de connaissances
            vector_store: Instance du vector store
            llm_config: Configuration LLM
            tools_config: Configuration des outils
            agent_config: Configuration de l'agent
            format: Format d'export ('json' ou 'yaml')
            filename: Nom du fichier (optionnel)
            
        Returns:
            str: Chemin du fichier exporté
        """
        try:
            # Collecte des données de configuration
            config_data = self._collect_configuration_data(
                rule_engine, knowledge_base, vector_store, 
                llm_config, tools_config, agent_config
            )
            
            # Génération du nom de fichier
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"business_config_{timestamp}.{format}"
            
            filepath = self.config_dir / filename
            
            # Export selon le format
            if format.lower() == 'json':
                self._export_json(config_data, filepath)
            elif format.lower() == 'yaml':
                self._export_yaml(config_data, filepath)
            else:
                raise ValueError(f"Format non supporté: {format}")
            
            self.logger.info(f"Configuration exportée: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export: {e}")
            raise
    
    def import_configuration(self, filepath: str) -> Dict[str, Any]:
        """
        Importe une configuration depuis un fichier
        
        Args:
            filepath: Chemin vers le fichier de configuration
            
        Returns:
            Dict: Configuration importée
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                raise FileNotFoundError(f"Fichier non trouvé: {filepath}")
            
            # Import selon l'extension
            if filepath.suffix.lower() == '.json':
                config_data = self._import_json(filepath)
            elif filepath.suffix.lower() in ['.yaml', '.yml']:
                config_data = self._import_yaml(filepath)
            else:
                raise ValueError(f"Format de fichier non supporté: {filepath.suffix}")
            
            self.logger.info(f"Configuration importée: {filepath}")
            return config_data
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'import: {e}")
            raise
    
    def apply_configuration(self, config_data: Dict[str, Any], 
                          rule_engine, knowledge_base, vector_store) -> bool:
        """
        Applique une configuration importée aux composants du système
        
        Args:
            config_data: Configuration à appliquer
            rule_engine: Instance du moteur de règles
            knowledge_base: Instance de la base de connaissances
            vector_store: Instance du vector store
            
        Returns:
            bool: True si succès
        """
        try:
            # Application de la configuration du moteur de règles
            if 'rule_engine' in config_data:
                self._apply_rule_engine_config(config_data['rule_engine'], rule_engine)
            
            # Application de la configuration de la base de connaissances
            if 'knowledge_base' in config_data:
                self._apply_knowledge_base_config(config_data['knowledge_base'], knowledge_base)
            
            # Application de la configuration du vector store
            if 'vector_store' in config_data:
                self._apply_vector_store_config(config_data['vector_store'], vector_store)
            
            self.logger.info("Configuration appliquée avec succès")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'application: {e}")
            return False
    
    def list_configurations(self) -> List[Dict[str, Any]]:
        """
        Liste toutes les configurations disponibles
        
        Returns:
            List: Liste des configurations avec métadonnées
        """
        configs = []
        
        for filepath in self.config_dir.glob("*"):
            if filepath.suffix.lower() in ['.json', '.yaml', '.yml']:
                try:
                    config_data = self.import_configuration(str(filepath))
                    configs.append({
                        'filename': filepath.name,
                        'filepath': str(filepath),
                        'name': config_data.get('name', 'Sans nom'),
                        'description': config_data.get('description', ''),
                        'version': config_data.get('version', '1.0'),
                        'created_at': config_data.get('created_at', ''),
                        'updated_at': config_data.get('updated_at', ''),
                        'format': filepath.suffix.lower(),
                        'size': filepath.stat().st_size
                    })
                except Exception as e:
                    self.logger.warning(f"Impossible de lire {filepath}: {e}")
        
        return sorted(configs, key=lambda x: x['updated_at'], reverse=True)
    
    def _collect_configuration_data(self, rule_engine, knowledge_base, vector_store,
                                  llm_config, tools_config, agent_config) -> Dict[str, Any]:
        """Collecte toutes les données de configuration"""
        
        # Configuration du moteur de règles
        rule_engine_config = {
            'business_rules': [],
            'statistics': rule_engine.get_statistics() if hasattr(rule_engine, 'get_statistics') else {},
            'templates': rule_engine.rule_templates if hasattr(rule_engine, 'rule_templates') else {}
        }
        
        if hasattr(rule_engine, 'business_rules'):
            for rule in rule_engine.business_rules:
                rule_engine_config['business_rules'].append({
                    'name': rule.name,
                    'description': rule.description,
                    'conditions': rule.conditions,
                    'actions': rule.actions,
                    'priority': rule.priority,
                    'category': rule.category,
                    'enabled': rule.enabled,
                    'created_at': rule.created_at.isoformat() if rule.created_at else None
                })
        
        # Configuration de la base de connaissances
        kb_config = {
            'ontology_classes': [],
            'instances': [],
            'business_handlers': []
        }
        
        if hasattr(knowledge_base, 'introspect_ontology'):
            kb_introspection = knowledge_base.introspect_ontology()
            kb_config['ontology_classes'] = kb_introspection.get('classes', [])
        
        if hasattr(knowledge_base, 'list_business_handlers'):
            kb_config['business_handlers'] = knowledge_base.list_business_handlers()
        
        # Configuration du vector store
        vs_config = {
            'collections': [],
            'statistics': {}
        }
        
        if hasattr(vector_store, 'list_collections'):
            vs_config['collections'] = vector_store.list_collections()
        
        # Configuration LLM par défaut
        default_llm_config = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 1000,
            'api_key_configured': False
        }
        
        # Configuration des outils par défaut
        default_tools_config = {
            'stock_api': {
                'enabled': True,
                'endpoint': 'http://localhost:5001/api/tools/stock'
            },
            'payment_api': {
                'enabled': True,
                'endpoint': 'http://localhost:5001/api/tools/payment'
            },
            'delivery_api': {
                'enabled': True,
                'endpoint': 'http://localhost:5001/api/tools/delivery'
            }
        }
        
        # Configuration de l'agent par défaut
        default_agent_config = {
            'intent_patterns': {},
            'fallback_enabled': True,
            'confidence_threshold': 0.7
        }
        
        # Création de la configuration complète
        config = BusinessConfig(
            name="Configuration Métier - Système de Gestion Cognitif",
            description="Configuration complète du système de gestion cognitif de commande",
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            rule_engine=rule_engine_config,
            knowledge_base=kb_config,
            vector_store=vs_config,
            llm_config=llm_config or default_llm_config,
            tools_config=tools_config or default_tools_config,
            agent_config=agent_config or default_agent_config,
            metadata={
                'exported_by': 'ConfigurationManager',
                'system_version': '1.0.0',
                'components': ['rule_engine', 'knowledge_base', 'vector_store', 'llm', 'tools', 'agent']
            }
        )
        
        return asdict(config)
    
    def _export_json(self, config_data: Dict[str, Any], filepath: Path):
        """Export en format JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def _export_yaml(self, config_data: Dict[str, Any], filepath: Path):
        """Export en format YAML"""
        try:
            import yaml
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        except ImportError:
            raise ImportError("PyYAML n'est pas installé. Installez-le avec: pip install PyYAML")
    
    def _import_json(self, filepath: Path) -> Dict[str, Any]:
        """Import depuis un fichier JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _import_yaml(self, filepath: Path) -> Dict[str, Any]:
        """Import depuis un fichier YAML"""
        try:
            import yaml
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except ImportError:
            raise ImportError("PyYAML n'est pas installé. Installez-le avec: pip install PyYAML")
    
    def _apply_rule_engine_config(self, config: Dict[str, Any], rule_engine):
        """Applique la configuration du moteur de règles"""
        try:
            # Suppression des règles existantes
            if hasattr(rule_engine, 'business_rules'):
                rule_engine.business_rules.clear()
            
            # Ajout des nouvelles règles
            if 'business_rules' in config:
                from src.core.rule_engine import BusinessRule
                from datetime import datetime
                
                for rule_data in config['business_rules']:
                    # Conversion des conditions et actions au format attendu
                    conditions = self._convert_conditions_to_list(rule_data.get('conditions', {}))
                    actions = self._convert_actions_to_list(rule_data.get('actions', []))
                    
                    # Gestion de la date de création
                    created_at = None
                    if 'created_at' in rule_data:
                        try:
                            created_at = datetime.fromisoformat(rule_data['created_at'].replace('Z', '+00:00'))
                        except:
                            created_at = datetime.now()
                    
                    rule = BusinessRule(
                        name=rule_data['name'],
                        description=rule_data['description'],
                        conditions=conditions,
                        actions=actions,
                        priority=rule_data.get('priority', 1),
                        category=rule_data.get('category', 'default'),
                        enabled=rule_data.get('enabled', True),
                        created_at=created_at
                    )
                    rule_engine.add_business_rule(rule)
                    
                    self.logger.info(f"Règle importée: {rule.name}")
            
            # Application des templates si disponibles
            if 'templates' in config and hasattr(rule_engine, 'rule_templates'):
                rule_engine.rule_templates.update(config['templates'])
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'application de la configuration du moteur de règles: {e}")
            raise
    
    def _convert_conditions_to_list(self, conditions_dict: Dict[str, Any]) -> List[str]:
        """Convertit les conditions du format YAML vers le format liste"""
        conditions = []
        
        for key, value in conditions_dict.items():
            if isinstance(value, dict):
                # Condition avec opérateur (ex: amount: {operator: ">=", value: 50})
                if 'operator' in value and 'value' in value:
                    conditions.append(f"{key} {value['operator']} {value['value']}")
                else:
                    # Condition complexe
                    conditions.append(f"{key}: {json.dumps(value)}")
            else:
                # Condition simple
                conditions.append(f"{key}: {value}")
        
        return conditions
    
    def _convert_actions_to_list(self, actions_list: List[Dict[str, Any]]) -> List[str]:
        """Convertit les actions du format YAML vers le format liste"""
        actions = []
        
        for action_data in actions_list:
            if isinstance(action_data, dict):
                action_name = action_data.get('action', '')
                params = action_data.get('params', {})
                
                if params:
                    # Action avec paramètres
                    param_str = ', '.join([f"{k}={v}" for k, v in params.items()])
                    actions.append(f"{action_name}({param_str})")
                else:
                    # Action simple
                    actions.append(action_name)
            else:
                # Action sous forme de string
                actions.append(str(action_data))
        
        return actions
    
    def _apply_knowledge_base_config(self, config: Dict[str, Any], knowledge_base):
        """Applique la configuration de la base de connaissances"""
        try:
            # Application des classes d'ontologie
            if 'ontology_classes' in config:
                for class_data in config['ontology_classes']:
                    if hasattr(knowledge_base, 'extend_ontology_dynamically'):
                        class_name = class_data['name']
                        properties_raw = class_data.get('properties', [])
                        
                        # Conversion des propriétés au format attendu
                        properties = self._convert_properties_format(properties_raw)
                        
                        # Ajout de la classe à l'ontologie
                        success = knowledge_base.extend_ontology_dynamically(class_name, properties)
                        
                        if success:
                            self.logger.info(f"Classe d'ontologie importée: {class_name}")
                        else:
                            self.logger.warning(f"Échec de l'import de la classe: {class_name}")
            
            # Application des gestionnaires métier
            if 'business_handlers' in config and hasattr(knowledge_base, 'add_business_handler'):
                for handler_data in config['business_handlers']:
                    handler_name = handler_data['name']
                    handler_description = handler_data.get('description', '')
                    methods = handler_data.get('methods', [])
                    
                    # Création de la configuration du handler
                    handler_config = {
                        'description': handler_description,
                        'methods': methods
                    }
                    
                    # Ajout du gestionnaire
                    knowledge_base.add_business_handler(handler_name, handler_config)
                    self.logger.info(f"Gestionnaire métier importé: {handler_name}")
                    
        except Exception as e:
            self.logger.error(f"Erreur lors de l'application de la configuration de la base de connaissances: {e}")
            raise
    
    def _convert_properties_format(self, properties_raw: List) -> List[Dict[str, Any]]:
        """Convertit les propriétés du format YAML vers le format attendu par extend_ontology_dynamically"""
        properties = []
        
        for prop in properties_raw:
            if isinstance(prop, str):
                # Propriété simple sous forme de string
                properties.append({
                    'name': prop,
                    'type': 'string',
                    'label': prop
                })
            elif isinstance(prop, dict):
                # Propriété déjà au bon format
                properties.append(prop)
            else:
                # Autre format, conversion en string
                properties.append({
                    'name': str(prop),
                    'type': 'string',
                    'label': str(prop)
                })
        
        return properties
    
    def _apply_vector_store_config(self, config: Dict[str, Any], vector_store):
        """Applique la configuration du vector store"""
        # Configuration des collections si nécessaire
        if 'collections' in config and hasattr(vector_store, 'configure_collections'):
            vector_store.configure_collections(config['collections'])


# Instance globale du gestionnaire de configuration
config_manager = ConfigurationManager()


if __name__ == "__main__":
    # Test du gestionnaire de configuration
    print("🧪 Test du Gestionnaire de Configuration")
    
    # Test d'export
    test_config = {
        'name': 'Test Config',
        'version': '1.0.0',
        'rule_engine': {'rules': []},
        'knowledge_base': {'classes': []},
        'vector_store': {'collections': []},
        'llm_config': {'model': 'gpt-3.5-turbo'},
        'tools_config': {'enabled': True},
        'agent_config': {'enabled': True},
        'metadata': {'test': True}
    }
    
    # Création d'un fichier de test
    test_file = config_manager.config_dir / "test_config.json"
    with open(test_file, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    # Test d'import
    imported_config = config_manager.import_configuration(str(test_file))
    print(f"✅ Configuration importée: {imported_config['name']}")
    
    # Liste des configurations
    configs = config_manager.list_configurations()
    print(f"📋 Configurations disponibles: {len(configs)}")
    
    # Nettoyage
    test_file.unlink()
    print("🧹 Test terminé") 