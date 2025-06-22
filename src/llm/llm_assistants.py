"""
Assistants LLM pour la génération automatique de workflows, patterns d'extraction et règles métier
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from src.llm.llm_interface import LLMInterface

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Représente une étape d'un workflow"""
    step: int
    action: str
    params: List[str]
    description: str
    conditions: Optional[List[str]] = None


@dataclass
class ExtractionPattern:
    """Représente un pattern d'extraction"""
    parameter_name: str
    patterns: List[str]
    description: str
    examples: List[str]


@dataclass
class BusinessRule:
    """Représente une règle métier"""
    condition: str
    action: str
    description: str
    priority: int = 1


class LLMAssistant:
    """Assistant LLM de base pour la génération automatique"""
    
    def __init__(self, llm_interface=None):
        self.llm_interface = llm_interface
        self.logger = logging.getLogger(__name__)
        
        # Initialisation des assistants spécialisés
        self.workflow_generator = WorkflowAssistant(llm_interface)
        self.pattern_generator = PatternAssistant(llm_interface)
        self.rule_generator = RuleAssistant(llm_interface)
    
    def configure(self, api_key: str = None, model: str = "gpt-4", temperature: float = 0.7):
        """Configure l'assistant LLM"""
        try:
            if api_key and self.llm_interface:
                self.llm_interface.configure(api_key=api_key, model=model, temperature=temperature)
            self.logger.info("Assistant LLM configuré avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration: {e}")
    
    def generate_workflow(self, domain: str, business_context: str) -> List[Dict]:
        """
        Génère automatiquement un workflow pour un domaine et contexte métier
        
        Args:
            domain: Domaine métier (ex: 'e-commerce', 'healthcare')
            business_context: Contexte métier détaillé
            
        Returns:
            List[Dict]: Workflow généré au format JSON
        """
        try:
            # Utilise l'assistant spécialisé
            workflow_steps = self.workflow_generator.generate_workflow_from_domain(domain, business_context)
            
            # Conversion en format JSON
            workflow_json = []
            for step in workflow_steps:
                workflow_json.append({
                    "step": step.step,
                    "action": step.action,
                    "params": step.params,
                    "description": step.description,
                    "conditions": step.conditions or []
                })
            
            return workflow_json
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du workflow: {e}")
            return self._generate_default_workflow_json(domain)
    
    def generate_extraction_patterns(self, entity_type: str, sample_data: str) -> List[Dict]:
        """
        Génère automatiquement des patterns d'extraction pour un type d'entité
        
        Args:
            entity_type: Type d'entité (ex: 'Client', 'Produit')
            sample_data: Données d'exemple
            
        Returns:
            List[Dict]: Patterns d'extraction générés au format JSON
        """
        try:
            # Utilise l'assistant spécialisé
            patterns = self.pattern_generator.generate_patterns_for_entity(entity_type, sample_data)
            
            # Conversion en format JSON
            patterns_json = []
            for pattern in patterns:
                patterns_json.append({
                    "name": pattern.parameter_name,
                    "patterns": pattern.patterns,
                    "description": pattern.description,
                    "examples": pattern.examples
                })
            
            return patterns_json
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des patterns: {e}")
            return self._generate_default_patterns_json(entity_type)
    
    def generate_business_rules(self, business_scenario: str, constraints: List[str]) -> List[Dict]:
        """
        Génère automatiquement des règles métier pour un scénario
        
        Args:
            business_scenario: Scénario métier détaillé
            constraints: Liste des contraintes métier
            
        Returns:
            List[Dict]: Règles métier générées au format JSON
        """
        try:
            # Utilise l'assistant spécialisé
            rules = self.rule_generator.generate_rules_for_scenario(business_scenario, constraints)
            
            # Conversion en format JSON
            rules_json = []
            for rule in rules:
                rules_json.append({
                    "name": f"Règle_{rule.priority}_{hash(rule.condition) % 1000}",
                    "condition": rule.condition,
                    "action": rule.action,
                    "description": rule.description,
                    "priority": rule.priority
                })
            
            return rules_json
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des règles: {e}")
            return self._generate_default_rules_json(business_scenario)
    
    def _generate_default_workflow_json(self, domain: str) -> List[Dict]:
        """Génère un workflow par défaut au format JSON"""
        return [
            {
                "step": 1,
                "action": "validate_input",
                "params": ["user_input"],
                "description": "Validation des données d'entrée",
                "conditions": []
            },
            {
                "step": 2,
                "action": "process_business_logic",
                "params": ["validated_data"],
                "description": f"Traitement de la logique métier pour {domain}",
                "conditions": []
            },
            {
                "step": 3,
                "action": "generate_response",
                "params": ["processed_data"],
                "description": "Génération de la réponse",
                "conditions": []
            }
        ]
    
    def _generate_default_patterns_json(self, entity_type: str) -> List[Dict]:
        """Génère des patterns par défaut au format JSON"""
        return [
            {
                "name": f"{entity_type.lower()}_name",
                "patterns": [r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"],
                "description": f"Extraction du nom de {entity_type}",
                "examples": [f"Nom: Jean Dupont"]
            },
            {
                "name": f"{entity_type.lower()}_id",
                "patterns": [r"ID[:\s]*([A-Z0-9-]+)", r"([A-Z0-9]{8,})"],
                "description": f"Extraction de l'ID de {entity_type}",
                "examples": [f"ID: {entity_type.upper()}-001"]
            }
        ]
    
    def _generate_default_rules_json(self, business_scenario: str) -> List[Dict]:
        """Génère des règles par défaut au format JSON"""
        return [
            {
                "name": "Règle_validation_001",
                "condition": "input_data is not None",
                "action": "validate_input",
                "description": "Validation des données d'entrée",
                "priority": 1
            },
            {
                "name": "Règle_traitement_001",
                "condition": "validated_data is not None",
                "action": "process_business_logic",
                "description": f"Traitement pour le scénario: {business_scenario[:50]}...",
                "priority": 2
            }
        ]


class WorkflowAssistant:
    def __init__(self, llm_interface=None):
        self.llm_interface = llm_interface
        self.logger = logging.getLogger(__name__)
        self.workflow_templates = self._load_workflow_templates()
    
    def generate_workflow_from_domain(self, domain: str, business_context: str) -> List[WorkflowStep]:
        """Génère un workflow pour un domaine et contexte métier"""
        try:
            # Utilise les templates du domaine
            domain_templates = self.workflow_templates.get(domain, [])
            
            if domain_templates:
                # Utilise le premier template du domaine
                template = domain_templates[0]
                return self._create_workflow_from_template(template, business_context)
            else:
                # Workflow générique
                return self._generate_generic_workflow(domain, business_context)
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du workflow: {e}")
            return self._generate_generic_workflow(domain, business_context)
    
    def generate_workflow_from_template(self, template_name: str, 
                                      parameters: Dict[str, Any]) -> List[WorkflowStep]:
        """Génère un workflow à partir d'un template spécifique"""
        template = self.workflow_templates.get(template_name, [])
        if template:
            return self._create_workflow_from_template(template[0], parameters)
        else:
            return self._generate_generic_workflow("generic", parameters)
    
    def is_available(self) -> bool:
        """Vérifie si l'assistant est disponible"""
        return True  # Toujours disponible en mode simulation
    
    def get_templates(self) -> List[Dict]:
        """Récupère les templates disponibles"""
        return list(self.workflow_templates.keys())
    
    def validate_output(self, content: str) -> Dict:
        """Valide la sortie d'un workflow"""
        try:
            # Validation basique
            if isinstance(content, dict) and 'steps' in content:
                return {
                    'is_valid': True,
                    'errors': [],
                    'warnings': []
                }
            else:
                return {
                    'is_valid': False,
                    'errors': ['Format de workflow invalide'],
                    'warnings': []
                }
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    def _create_workflow_from_template(self, template: Dict, context: str) -> List[WorkflowStep]:
        """Crée un workflow à partir d'un template"""
        steps = []
        for i, step_data in enumerate(template.get('steps', []), 1):
            step = WorkflowStep(
                step=i,
                action=step_data.get('action', f'step_{i}'),
                params=step_data.get('params', []),
                description=step_data.get('description', ''),
                conditions=step_data.get('conditions', [])
            )
            steps.append(step)
        return steps
    
    def _generate_generic_workflow(self, domain: str, context: str) -> List[WorkflowStep]:
        """Génère un workflow générique"""
        return [
            WorkflowStep(
                step=1,
                action="validate_input",
                params=["user_input"],
                description=f"Validation des données d'entrée pour {domain}",
                conditions=[]
            ),
            WorkflowStep(
                step=2,
                action="process_business_logic",
                params=["validated_data"],
                description=f"Traitement de la logique métier {domain}",
                conditions=[]
            ),
            WorkflowStep(
                step=3,
                action="generate_response",
                params=["processed_data"],
                description="Génération de la réponse",
                conditions=[]
            )
        ]
    
    def _load_workflow_templates(self) -> Dict[str, List[Dict]]:
        """Charge les templates de workflows par domaine"""
        return {
            'ecommerce': [
                {
                    'name': 'order_processing',
                    'steps': [
                        {
                            'action': 'validate_customer',
                            'params': ['customer_id'],
                            'description': 'Validation du client',
                            'conditions': ['customer_exists']
                        },
                        {
                            'action': 'check_stock',
                            'params': ['product_id', 'quantity'],
                            'description': 'Vérification du stock',
                            'conditions': ['product_available']
                        },
                        {
                            'action': 'calculate_price',
                            'params': ['product_id', 'quantity'],
                            'description': 'Calcul du prix',
                            'conditions': []
                        },
                        {
                            'action': 'process_payment',
                            'params': ['amount', 'payment_method'],
                            'description': 'Traitement du paiement',
                            'conditions': ['payment_valid']
                        },
                        {
                            'action': 'create_order',
                            'params': ['order_data'],
                            'description': 'Création de la commande',
                            'conditions': ['payment_successful']
                        }
                    ]
                }
            ],
            'healthcare': [
                {
                    'name': 'patient_consultation',
                    'steps': [
                        {
                            'action': 'validate_patient',
                            'params': ['patient_id'],
                            'description': 'Validation du patient',
                            'conditions': ['patient_exists']
                        },
                        {
                            'action': 'check_appointment',
                            'params': ['appointment_id'],
                            'description': 'Vérification du rendez-vous',
                            'conditions': ['appointment_valid']
                        },
                        {
                            'action': 'conduct_consultation',
                            'params': ['patient_data'],
                            'description': 'Conduite de la consultation',
                            'conditions': []
                        },
                        {
                            'action': 'update_records',
                            'params': ['consultation_data'],
                            'description': 'Mise à jour des dossiers',
                            'conditions': ['consultation_complete']
                        }
                    ]
                }
            ]
        }


class PatternAssistant:
    def __init__(self, llm_interface=None):
        self.llm_interface = llm_interface
        self.logger = logging.getLogger(__name__)
        self.pattern_templates = self._load_pattern_templates()
    
    def generate_patterns_for_entity(self, entity_type: str, sample_data: str) -> List[ExtractionPattern]:
        """Génère des patterns pour un type d'entité avec des données d'exemple"""
        try:
            # Analyse des données d'exemple pour générer des patterns adaptés
            patterns = []
            
            # Pattern pour le nom
            patterns.append(ExtractionPattern(
                parameter_name=f"{entity_type.lower()}_name",
                patterns=[r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"],
                description=f"Extraction du nom de {entity_type}",
                examples=[f"Nom: Jean Dupont"]
            ))
            
            # Pattern pour l'ID
            patterns.append(ExtractionPattern(
                parameter_name=f"{entity_type.lower()}_id",
                patterns=[r"ID[:\s]*([A-Z0-9-]+)", r"([A-Z0-9]{8,})"],
                description=f"Extraction de l'ID de {entity_type}",
                examples=[f"ID: {entity_type.upper()}-001"]
            ))
            
            # Patterns spécifiques selon le type d'entité
            if entity_type.lower() in ['client', 'customer']:
                patterns.extend(self._generate_client_patterns(sample_data))
            elif entity_type.lower() in ['product', 'produit']:
                patterns.extend(self._generate_product_patterns(sample_data))
            elif entity_type.lower() in ['order', 'commande']:
                patterns.extend(self._generate_order_patterns(sample_data))
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des patterns: {e}")
            return self._generate_default_patterns([entity_type])
    
    def generate_patterns_for_domain(self, domain: str, 
                                   parameters: List[str]) -> List[ExtractionPattern]:
        """Génère des patterns adaptés à un domaine spécifique"""
        domain_templates = self.pattern_templates.get(domain, {})
        
        patterns = []
        for param in parameters:
            if param in domain_templates:
                template = domain_templates[param]
                pattern = ExtractionPattern(
                    parameter_name=param,
                    patterns=template['patterns'],
                    description=template['description'],
                    examples=template['examples']
                )
            else:
                # Pattern générique
                pattern = ExtractionPattern(
                    parameter_name=param,
                    patterns=[f"{param}: (.+)"],
                    description=f"Extraction de {param}",
                    examples=[f"{param}: valeur"]
                )
            patterns.append(pattern)
        
        return patterns
    
    def is_available(self) -> bool:
        """Vérifie si l'assistant est disponible"""
        return True  # Toujours disponible en mode simulation
    
    def get_templates(self) -> List[Dict]:
        """Récupère les templates disponibles"""
        return list(self.pattern_templates.keys())
    
    def validate_output(self, content: str) -> Dict:
        """Valide la sortie d'un pattern"""
        try:
            # Validation basique
            if isinstance(content, dict) and 'patterns' in content:
                return {
                    'is_valid': True,
                    'errors': [],
                    'warnings': []
                }
            else:
                return {
                    'is_valid': False,
                    'errors': ['Format de pattern invalide'],
                    'warnings': []
                }
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    def _generate_client_patterns(self, sample_data: str) -> List[ExtractionPattern]:
        """Génère des patterns spécifiques aux clients"""
        return [
            ExtractionPattern(
                parameter_name="email",
                patterns=[r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"],
                description="Extraction de l'email",
                examples=["jean.dupont@email.com"]
            ),
            ExtractionPattern(
                parameter_name="phone",
                patterns=[r"(\+?[0-9\s\-\(\)]{10,})"],
                description="Extraction du téléphone",
                examples=["+33 1 23 45 67 89"]
            )
        ]
    
    def _generate_product_patterns(self, sample_data: str) -> List[ExtractionPattern]:
        """Génère des patterns spécifiques aux produits"""
        return [
            ExtractionPattern(
                parameter_name="price",
                patterns=[r"(\d+(?:\.\d{2})?)\s*€", r"prix[:\s]*(\d+(?:\.\d{2})?)"],
                description="Extraction du prix",
                examples=["29.99€", "prix: 45.50"]
            ),
            ExtractionPattern(
                parameter_name="category",
                patterns=[r"catégorie[:\s]*([a-zA-Z\s]+)", r"([a-zA-Z\s]+)\s+catégorie"],
                description="Extraction de la catégorie",
                examples=["catégorie: Électronique"]
            )
        ]
    
    def _generate_order_patterns(self, sample_data: str) -> List[ExtractionPattern]:
        """Génère des patterns spécifiques aux commandes"""
        return [
            ExtractionPattern(
                parameter_name="quantity",
                patterns=[r"(\d+)\s+unités?", r"quantité[:\s]*(\d+)"],
                description="Extraction de la quantité",
                examples=["3 unités", "quantité: 5"]
            ),
            ExtractionPattern(
                parameter_name="total",
                patterns=[r"total[:\s]*(\d+(?:\.\d{2})?)\s*€", r"(\d+(?:\.\d{2})?)\s*€\s+total"],
                description="Extraction du total",
                examples=["total: 89.99€"]
            )
        ]
    
    def _load_pattern_templates(self) -> Dict[str, Dict[str, Dict]]:
        """Charge les templates de patterns par domaine"""
        return {
            'ecommerce': {
                'product_name': {
                    'patterns': [
                        r'produit\s+([a-zA-Z\s]+)',
                        r'commander\s+([a-zA-Z\s]+)',
                        r'acheter\s+([a-zA-Z\s]+)'
                    ],
                    'description': 'Extraction du nom du produit',
                    'examples': ['produit iPhone', 'commander Samsung Galaxy']
                },
                'quantity': {
                    'patterns': [
                        r'(\d+)\s+unités?',
                        r'quantité\s*[:=]\s*(\d+)',
                        r'(\d+)\s+fois'
                    ],
                    'description': 'Extraction de la quantité',
                    'examples': ['3 unités', 'quantité: 5']
                },
                'price': {
                    'patterns': [
                        r'(\d+(?:\.\d{2})?)\s*€',
                        r'prix\s*[:=]\s*(\d+(?:\.\d{2})?)',
                        r'(\d+(?:\.\d{2})?)\s+euros?'
                    ],
                    'description': 'Extraction du prix',
                    'examples': ['29.99€', 'prix: 45.50']
                }
            },
            'restaurant': {
                'date': {
                    'patterns': [
                        r'(\d{1,2}/\d{1,2}/\d{4})',
                        r'(\d{1,2}-\d{1,2}-\d{4})',
                        r'pour\s+le\s+(\d{1,2}\s+[a-zA-Z]+)'
                    ],
                    'description': 'Extraction de la date',
                    'examples': ['15/12/2024', 'pour le 20 décembre']
                },
                'time': {
                    'patterns': [
                        r'(\d{1,2}:\d{2})',
                        r'à\s+(\d{1,2}h\d{2})',
                        r'(\d{1,2})\s+heures?'
                    ],
                    'description': 'Extraction de l\'heure',
                    'examples': ['19:30', 'à 20h00']
                },
                'guests': {
                    'patterns': [
                        r'(\d+)\s+personnes?',
                        r'pour\s+(\d+)\s+personnes?',
                        r'table\s+pour\s+(\d+)'
                    ],
                    'description': 'Extraction du nombre de personnes',
                    'examples': ['4 personnes', 'table pour 6']
                }
            }
        }


class RuleAssistant:
    def __init__(self, llm_interface=None):
        self.llm_interface = llm_interface
        self.logger = logging.getLogger(__name__)
        self.rule_templates = self._load_rule_templates()
    
    def generate_rules_for_scenario(self, business_scenario: str, constraints: List[str]) -> List[BusinessRule]:
        """Génère des règles métier pour un scénario et des contraintes"""
        try:
            rules = []
            
            # Règles de base pour le scénario
            rules.append(BusinessRule(
                condition="input_data is not None",
                action="validate_input",
                description="Validation des données d'entrée",
                priority=1
            ))
            
            # Règles basées sur les contraintes
            for i, constraint in enumerate(constraints, 2):
                rules.append(BusinessRule(
                    condition=f"check_constraint_{i}",
                    action="apply_constraint",
                    description=f"Application de la contrainte: {constraint[:50]}...",
                    priority=i
                ))
            
            # Règles spécifiques au scénario
            if "commande" in business_scenario.lower():
                rules.extend(self._generate_order_rules())
            elif "paiement" in business_scenario.lower():
                rules.extend(self._generate_payment_rules())
            elif "validation" in business_scenario.lower():
                rules.extend(self._generate_validation_rules())
            
            return rules
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des règles: {e}")
            return self._generate_default_rules(business_scenario)
    
    def generate_rules_for_domain(self, domain: str, 
                                business_context: str) -> List[BusinessRule]:
        """Génère des règles métier adaptées à un domaine"""
        domain_rules = self.rule_templates.get(domain, [])
        
        # Personnalisation des règles avec le contexte
        rules = []
        for rule_template in domain_rules:
            rule = BusinessRule(
                condition=rule_template['condition'],
                action=rule_template['action'],
                description=rule_template['description'],
                priority=rule_template.get('priority', 1)
            )
            rules.append(rule)
        
        return rules
    
    def is_available(self) -> bool:
        """Vérifie si l'assistant est disponible"""
        return True  # Toujours disponible en mode simulation
    
    def get_templates(self) -> List[Dict]:
        """Récupère les templates disponibles"""
        return list(self.rule_templates.keys())
    
    def validate_output(self, content: str) -> Dict:
        """Valide la sortie d'une règle"""
        try:
            # Validation basique
            if isinstance(content, dict) and 'rules' in content:
                return {
                    'is_valid': True,
                    'errors': [],
                    'warnings': []
                }
            else:
                return {
                    'is_valid': False,
                    'errors': ['Format de règle invalide'],
                    'warnings': []
                }
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    def _generate_order_rules(self) -> List[BusinessRule]:
        """Génère des règles spécifiques aux commandes"""
        return [
            BusinessRule(
                condition="order_amount > 1000",
                action="require_approval",
                description="Approbation requise pour commandes > 1000€",
                priority=2
            ),
            BusinessRule(
                condition="stock_available == False",
                action="reject_order",
                description="Rejet de commande si stock insuffisant",
                priority=3
            )
        ]
    
    def _generate_payment_rules(self) -> List[BusinessRule]:
        """Génère des règles spécifiques aux paiements"""
        return [
            BusinessRule(
                condition="payment_amount > 500",
                action="require_3d_secure",
                description="3D Secure requis pour paiements > 500€",
                priority=2
            ),
            BusinessRule(
                condition="payment_method == 'card'",
                action="validate_card",
                description="Validation de la carte de crédit",
                priority=3
            )
        ]
    
    def _generate_validation_rules(self) -> List[BusinessRule]:
        """Génère des règles de validation"""
        return [
            BusinessRule(
                condition="email_format_valid == False",
                action="reject_input",
                description="Rejet si format email invalide",
                priority=2
            ),
            BusinessRule(
                condition="required_fields_missing == True",
                action="request_completion",
                description="Demande de complétion des champs requis",
                priority=3
            )
        ]
    
    def _load_rule_templates(self) -> Dict[str, List[Dict]]:
        """Charge les templates de règles par domaine"""
        return {
            'ecommerce': [
                {
                    'condition': 'amount >= 100',
                    'action': 'apply_free_shipping',
                    'description': 'Livraison gratuite pour commandes >= 100€',
                    'priority': 1
                },
                {
                    'condition': 'customer_type == "fidèle"',
                    'action': 'apply_loyalty_discount',
                    'description': 'Remise fidélité pour clients fidèles',
                    'priority': 2
                },
                {
                    'condition': 'stock < 5',
                    'action': 'send_low_stock_alert',
                    'description': 'Alerte stock faible',
                    'priority': 3
                }
            ],
            'restaurant': [
                {
                    'condition': 'guests >= 8',
                    'action': 'require_advance_reservation',
                    'description': 'Réservation à l\'avance pour groupes >= 8',
                    'priority': 1
                },
                {
                    'condition': 'time == "peak_hours"',
                    'action': 'apply_peak_hour_pricing',
                    'description': 'Tarification heures de pointe',
                    'priority': 2
                }
            ]
        }


# Instance globale des assistants
workflow_assistant = WorkflowAssistant()
pattern_assistant = PatternAssistant()
rule_assistant = RuleAssistant()


if __name__ == "__main__":
    # Test des assistants
    print("🧪 Test des Assistants LLM")
    
    # Test de génération de workflow
    workflow = workflow_assistant.generate_workflow(
        "e-commerce",
        "Gestion des commandes en ligne"
    )
    print(f"📋 Workflow généré: {len(workflow)} étapes")
    
    # Test de génération de patterns
    patterns = pattern_assistant.generate_patterns_for_entity(
        "ecommerce",
        "Gestion des commandes en ligne"
    )
    print(f"🔍 Patterns générés: {len(patterns)} patterns")
    
    # Test de génération de règles
    rules = rule_assistant.generate_rules_for_scenario(
        "ecommerce",
        ["stock_available == False", "amount >= 100"]
    )
    print(f"⚖️ Règles générées: {len(rules)} règles")
    
    print("✅ Tests terminés") 