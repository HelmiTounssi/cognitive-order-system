"""
Moteur de Règles Avancé - Système de Gestion Cognitif de Commande
Utilise Pyke pour l'inférence de règles métier et la logique sémantique
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

# Simulation de Pyke (car Pyke n'est pas installé par défaut)
# En production, vous installeriez: pip install pyke
class PykeEngine:
    """Moteur de règles Pyke simulé pour l'inférence sémantique"""
    
    def __init__(self):
        self.rules = {}
        self.facts = {}
        self.inference_results = []
        self.logger = logging.getLogger(__name__)
        
    def add_rule(self, rule_name: str, conditions: List[str], actions: List[str], priority: int = 1):
        """Ajoute une règle au moteur"""
        self.rules[rule_name] = {
            'conditions': conditions,
            'actions': actions,
            'priority': priority,
            'created_at': datetime.now()
        }
        self.logger.info(f"Règle ajoutée: {rule_name}")
        
    def add_fact(self, fact_type: str, fact_data: Dict[str, Any]):
        """Ajoute un fait à la base de connaissances"""
        if fact_type not in self.facts:
            self.facts[fact_type] = []
        self.facts[fact_type].append(fact_data)
        self.logger.info(f"Fait ajouté: {fact_type}")
        
    def infer(self, query: str) -> List[Dict[str, Any]]:
        """Effectue l'inférence basée sur les règles et faits"""
        results = []
        
        # Analyse sémantique de la requête
        intent = self._extract_intent(query)
        entities = self._extract_entities(query)
        
        # Application des règles
        for rule_name, rule in self.rules.items():
            if self._evaluate_rule(rule, intent, entities):
                result = {
                    'rule_name': rule_name,
                    'intent': intent,
                    'entities': entities,
                    'actions': rule['actions'],
                    'confidence': self._calculate_confidence(rule, intent, entities),
                    'timestamp': datetime.now()
                }
                results.append(result)
                
        # Tri par priorité et confiance
        results.sort(key=lambda x: (x['confidence'], self.rules[x['rule_name']]['priority']), reverse=True)
        
        self.inference_results.extend(results)
        return results
    
    def _extract_intent(self, query: str) -> str:
        """Extrait l'intention de la requête"""
        query_lower = query.lower()
        
        intent_patterns = {
            'commander': ['commander', 'acheter', 'passer une commande', 'je veux'],
            'consulter': ['consulter', 'voir', 'afficher', 'montrer', 'status'],
            'annuler': ['annuler', 'supprimer', 'retirer', 'annulation'],
            'modifier': ['modifier', 'changer', 'ajuster', 'mise à jour'],
            'livraison': ['livrer', 'livraison', 'expédier', 'shipping'],
            'paiement': ['payer', 'paiement', 'facture', 'tarif']
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
                
        return 'general'
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extrait les entités de la requête"""
        entities = {
            'quantite': None,
            'produit': None,
            'client': None,
            'prix': None,
            'date': None,
            'adresse': None
        }
        
        # Extraction de quantité - patterns améliorés
        quantite_patterns = [
            r'(\d+)\s*(produit|article|item|unité|unités|laptop|souris|clavier)',
            r'commander\s+(\d+)',
            r'(\d+)\s+de\s+([a-zA-Z0-9\s]+)',
            r'(\d+)\s+([a-zA-Z0-9\s]+)'
        ]
        
        for pattern in quantite_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                entities['quantite'] = int(match.group(1))
                # Si on a aussi le produit dans le même match
                if len(match.groups()) > 1 and not entities['produit']:
                    entities['produit'] = match.group(2).strip()
                break
        
        # Extraction de produit - patterns améliorés
        if not entities['produit']:
            produit_patterns = [
                r'commander\s+([a-zA-Z0-9\s]+)',
                r'produit\s+([a-zA-Z0-9\s]+)',
                r'article\s+([a-zA-Z0-9\s]+)',
                r'([a-zA-Z0-9\s]+)\s+produit',
                r'([a-zA-Z0-9\s]+)\s+gaming',
                r'laptop\s+([a-zA-Z0-9\s]+)',
                r'souris\s+([a-zA-Z0-9\s]+)',
                r'clavier\s+([a-zA-Z0-9\s]+)'
            ]
            
            for pattern in produit_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    product_name = match.group(1).strip()
                    # Nettoyer le nom du produit
                    if product_name and len(product_name) > 2:
                        entities['produit'] = product_name
                        break
        
        # Extraction de prix
        prix_match = re.search(r'(\d+(?:\.\d{2})?)\s*(euro|€|eur)', query, re.IGNORECASE)
        if prix_match:
            entities['prix'] = float(prix_match.group(1))
        
        # Nettoyage des entités
        if entities['produit']:
            # Supprimer les mots de liaison
            stop_words = ['de', 'du', 'des', 'le', 'la', 'les', 'un', 'une', 'avec', 'et', 'ou']
            words = entities['produit'].split()
            clean_words = [word for word in words if word.lower() not in stop_words and len(word) > 1]
            if clean_words:
                entities['produit'] = ' '.join(clean_words)
            
        return entities
    
    def _evaluate_rule(self, rule: Dict, intent: str, entities: Dict) -> bool:
        """Évalue si une règle s'applique"""
        for condition in rule['conditions']:
            if not self._evaluate_condition(condition, intent, entities):
                return False
        return True
    
    def _evaluate_condition(self, condition: str, intent: str, entities: Dict) -> bool:
        """Évalue une condition de règle"""
        condition_lower = condition.lower()
        
        # Conditions d'intention
        if 'intent:' in condition_lower:
            required_intent = condition_lower.split('intent:')[1].strip()
            if intent != required_intent:
                return False
                
        # Conditions d'entités
        if 'has_quantity' in condition_lower:
            if not entities.get('quantite'):
                return False
                
        if 'has_product' in condition_lower:
            if not entities.get('produit'):
                return False
                
        if 'has_price' in condition_lower:
            if not entities.get('prix'):
                return False
                
        return True
    
    def _calculate_confidence(self, rule: Dict, intent: str, entities: Dict) -> float:
        """Calcule la confiance d'une règle"""
        confidence = 0.5  # Base confidence
        
        # Bonus pour correspondance d'intention
        if intent in str(rule['conditions']):
            confidence += 0.3
            
        # Bonus pour entités présentes
        entity_count = sum(1 for entity in entities.values() if entity is not None)
        confidence += min(entity_count * 0.1, 0.3)
        
        return min(confidence, 1.0)
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du moteur de règles"""
        return {
            'total_rules': len(self.rules),
            'total_facts': sum(len(facts) for facts in self.facts.values()),
            'total_inferences': len(self.inference_results),
            'rule_categories': self._get_rule_categories(),
            'performance_metrics': self._get_performance_metrics()
        }
    
    def _get_rule_categories(self) -> Dict[str, int]:
        """Groupe les règles par catégorie"""
        categories = {}
        for rule_name, rule in self.rules.items():
            category = rule_name.split('_')[0] if '_' in rule_name else 'general'
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Calcule les métriques de performance"""
        if not self.inference_results:
            return {'avg_confidence': 0, 'success_rate': 0}
            
        confidences = [result['confidence'] for result in self.inference_results]
        return {
            'avg_confidence': sum(confidences) / len(confidences),
            'success_rate': len([c for c in confidences if c > 0.7]) / len(confidences)
        }


@dataclass
class BusinessRule:
    """Représente une règle métier"""
    name: str
    description: str
    conditions: List[str]
    actions: List[str]
    priority: int
    category: str
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class AdvancedRuleEngine:
    """Moteur de règles avancé avec intégration des outils réels"""
    
    def __init__(self, knowledge_base=None, tools_manager=None):
        """
        Initialise le moteur de règles avancé
        
        Args:
            knowledge_base: Instance de KnowledgeBase pour accéder aux données
            tools_manager: Gestionnaire d'outils pour exécuter les actions
        """
        self.pyke_engine = PykeEngine()
        self.business_rules = []
        self.knowledge_base = knowledge_base
        self.tools_manager = tools_manager
        self.logger = logging.getLogger(__name__)
        
        # Charge les templates de règles
        self.rule_templates = self._load_rule_templates()
        
        # Initialise les règles par défaut
        self._initialize_default_rules()
        
    def _load_rule_templates(self) -> Dict[str, Dict]:
        """Charge les templates de règles prédéfinis"""
        return {
            'stock_management': {
                'name': 'Gestion Stock',
                'description': 'Vérification automatique du stock',
                'conditions': ['intent:commander', 'has_quantity', 'has_product'],
                'actions': ['check_stock'],
                'priority': 1,
                'category': 'stock'
            },
            'order_validation': {
                'name': 'Validation Commande',
                'description': 'Validation automatique des commandes',
                'conditions': ['intent:commander'],
                'actions': ['validate_order'],
                'priority': 2,
                'category': 'order'
            },
            'price_calculation': {
                'name': 'Calcul Prix',
                'description': 'Calcul automatique des prix',
                'conditions': ['intent:commander', 'has_quantity'],
                'actions': ['calculate_price'],
                'priority': 3,
                'category': 'pricing'
            },
            'express_delivery': {
                'name': 'Livraison Express',
                'description': 'Vérification de la livraison express',
                'conditions': ['intent:commander'],
                'actions': ['check_express_availability', 'calculate_express_cost'],
                'priority': 4,
                'category': 'delivery'
            },
            'payment_validation': {
                'name': 'Validation Paiement',
                'description': 'Validation des méthodes de paiement',
                'conditions': ['intent:commander'],
                'actions': ['validate_payment_method'],
                'priority': 5,
                'category': 'payment'
            },
            'security_checks': {
                'name': 'Vérifications Sécurité',
                'description': 'Vérifications de sécurité automatiques',
                'conditions': ['intent:commander'],
                'actions': ['apply_security_checks'],
                'priority': 6,
                'category': 'security'
            },
            'stock_alert': {
                'name': 'Alerte Stock',
                'description': 'Alertes de stock bas',
                'conditions': ['has_quantity', 'has_product'],
                'actions': ['check_stock_level', 'send_alert_if_low'],
                'priority': 3,
                'category': 'stock'
            }
        }
    
    def _initialize_default_rules(self):
        """Initialise les règles par défaut"""
        for template_name, template in self.rule_templates.items():
            rule = BusinessRule(
                name=template['name'],
                description=template['description'],
                conditions=template['conditions'],
                actions=template['actions'],
                priority=template['priority'],
                category=template['category']
            )
            self.add_business_rule(rule)
    
    def add_business_rule(self, rule: BusinessRule):
        """Ajoute une règle métier"""
        self.business_rules.append(rule)
        self.pyke_engine.add_rule(rule.name, rule.conditions, rule.actions, rule.priority)
        self.logger.info(f"Règle métier ajoutée: {rule.name}")
    
    def remove_business_rule(self, rule_name: str) -> bool:
        """Supprime une règle métier"""
        for i, rule in enumerate(self.business_rules):
            if rule.name == rule_name:
                del self.business_rules[i]
                if rule_name in self.pyke_engine.rules:
                    del self.pyke_engine.rules[rule_name]
                self.logger.info(f"Règle métier supprimée: {rule_name}")
                return True
        return False
    
    def update_business_rule(self, rule_name: str, updates: Dict[str, Any]) -> bool:
        """Met à jour une règle métier"""
        for rule in self.business_rules:
            if rule.name == rule_name:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                
                # Met à jour la règle dans le moteur Pyke
                if rule_name in self.pyke_engine.rules:
                    del self.pyke_engine.rules[rule_name]
                self.pyke_engine.add_rule(rule.name, rule.conditions, rule.actions, rule.priority)
                
                self.logger.info(f"Règle métier mise à jour: {rule_name}")
                return True
        return False
    
    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Traite une requête en appliquant les règles métier cognitives
        
        Args:
            query: Requête utilisateur
            context: Contexte supplémentaire
        
        Returns:
            Dict: Résultats de l'inférence
        """
        try:
            # Initialise le contexte
            if context is None:
                context = {}
            
            # Analyse sémantique de la requête
            intent = self._extract_intent(query)
            entities = self._extract_entities(query)
            
            # Applique les règles cognitives
            inference_results = []
            executed_actions = []
            
            for rule in self.business_rules:
                if rule.enabled and self._evaluate_rule(rule, intent, entities, context):
                    # Exécute les actions de la règle
                    for action in rule.actions:
                        action_result = self._execute_action(action, context, entities)
                        executed_actions.append({
                            'action': action,
                            'result': action_result,
                            'rule': rule.name
                        })
                    
                    inference_results.append({
                        'rule': rule.name,
                        'confidence': self._calculate_confidence(rule, intent, entities),
                        'timestamp': datetime.now()
                    })
            
            return {
                'intent': intent,
                'entities': entities,
                'inference_results': inference_results,
                'executed_actions': executed_actions,
                'confidence': self._calculate_overall_confidence(inference_results)
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement: {e}")
            return {'error': str(e)}
    
    def _extract_intent(self, query: str) -> str:
        """Extrait l'intention de la requête"""
        query_lower = query.lower()
        
        intent_patterns = {
            'commander': ['commander', 'acheter', 'passer une commande', 'je veux'],
            'consulter': ['consulter', 'voir', 'afficher', 'montrer', 'status'],
            'annuler': ['annuler', 'supprimer', 'retirer', 'annulation'],
            'modifier': ['modifier', 'changer', 'ajuster', 'mise à jour'],
            'livraison': ['livrer', 'livraison', 'expédier', 'shipping'],
            'paiement': ['payer', 'paiement', 'facture', 'tarif']
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
                
        return 'general'
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extrait les entités de la requête"""
        entities = {
            'quantite': None,
            'produit': None,
            'client': None,
            'prix': None,
            'date': None,
            'adresse': None
        }
        
        # Extraction de quantité - patterns améliorés
        quantite_patterns = [
            r'(\d+)\s*(produit|article|item|unité|unités|laptop|souris|clavier)',
            r'commander\s+(\d+)',
            r'(\d+)\s+de\s+([a-zA-Z0-9\s]+)',
            r'(\d+)\s+([a-zA-Z0-9\s]+)'
        ]
        
        for pattern in quantite_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                entities['quantite'] = int(match.group(1))
                # Si on a aussi le produit dans le même match
                if len(match.groups()) > 1 and not entities['produit']:
                    entities['produit'] = match.group(2).strip()
                break
        
        # Extraction de produit - patterns améliorés
        if not entities['produit']:
            produit_patterns = [
                r'commander\s+([a-zA-Z0-9\s]+)',
                r'produit\s+([a-zA-Z0-9\s]+)',
                r'article\s+([a-zA-Z0-9\s]+)',
                r'([a-zA-Z0-9\s]+)\s+produit',
                r'([a-zA-Z0-9\s]+)\s+gaming',
                r'laptop\s+([a-zA-Z0-9\s]+)',
                r'souris\s+([a-zA-Z0-9\s]+)',
                r'clavier\s+([a-zA-Z0-9\s]+)'
            ]
            
            for pattern in produit_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    product_name = match.group(1).strip()
                    # Nettoyer le nom du produit
                    if product_name and len(product_name) > 2:
                        entities['produit'] = product_name
                        break
        
        # Extraction de prix
        prix_match = re.search(r'(\d+(?:\.\d{2})?)\s*(euro|€|eur)', query, re.IGNORECASE)
        if prix_match:
            entities['prix'] = float(prix_match.group(1))
        
        # Nettoyage des entités
        if entities['produit']:
            # Supprimer les mots de liaison
            stop_words = ['de', 'du', 'des', 'le', 'la', 'les', 'un', 'une', 'avec', 'et', 'ou']
            words = entities['produit'].split()
            clean_words = [word for word in words if word.lower() not in stop_words and len(word) > 1]
            if clean_words:
                entities['produit'] = ' '.join(clean_words)
            
        return entities
    
    def _evaluate_rule(self, rule: BusinessRule, intent: str, entities: Dict, context: Dict) -> bool:
        """Évalue si une règle s'applique"""
        for condition in rule.conditions:
            if not self._evaluate_condition(condition, intent, entities, context):
                return False
        return True
    
    def _evaluate_condition(self, condition: str, intent: str, entities: Dict, context: Dict) -> bool:
        """Évalue une condition de règle"""
        condition_lower = condition.lower()
        
        # Conditions d'intention
        if 'intent:' in condition_lower:
            required_intent = condition_lower.split('intent:')[1].strip()
            if intent != required_intent:
                return False
                
        # Conditions d'entités
        if 'has_quantity' in condition_lower:
            if not entities.get('quantite'):
                return False
                
        if 'has_product' in condition_lower:
            if not entities.get('produit'):
                return False
                
        if 'has_price' in condition_lower:
            if not entities.get('prix'):
                return False
                
        return True
    
    def _calculate_confidence(self, rule: BusinessRule, intent: str, entities: Dict) -> float:
        """Calcule la confiance d'une règle"""
        confidence = 0.5  # Base confidence
        
        # Bonus pour correspondance d'intention
        if intent in str(rule.conditions):
            confidence += 0.3
            
        # Bonus pour entités présentes
        entity_count = sum(1 for entity in entities.values() if entity is not None)
        confidence += min(entity_count * 0.1, 0.3)
        
        return min(confidence, 1.0)
    
    def _calculate_overall_confidence(self, inference_results: List[Dict]) -> float:
        """Calcule la confiance globale"""
        if not inference_results:
            return 0.0
        confidences = [result['confidence'] for result in inference_results]
        return sum(confidences) / len(confidences)
    
    def _execute_action(self, action: str, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute une action spécifique en utilisant les vrais outils"""
        try:
            # Import des outils
            import tools
            
            # Mapping des actions vers les outils
            action_mapping = {
                'validate_order': self._execute_validate_order,
                'check_stock': self._execute_check_stock,
                'calculate_price': self._execute_calculate_price,
                'check_express_availability': self._execute_check_express_availability,
                'calculate_express_cost': self._execute_calculate_express_cost,
                'validate_payment_method': self._execute_validate_payment_method,
                'apply_security_checks': self._execute_apply_security_checks,
                'check_stock_level': self._execute_check_stock_level,
                'send_alert_if_low': self._execute_send_alert_if_low
            }
            
            handler = action_mapping.get(action)
            if handler:
                return handler(context, entities)
            else:
                return {'status': 'unknown_action', 'action': action}
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de l'action {action}: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _execute_validate_order(self, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Valide une commande en utilisant les outils"""
        try:
            if not self.knowledge_base:
                return {'status': 'error', 'error': 'Knowledge base not available'}
            
            # Récupère l'ID de commande du contexte ou génère un ID temporaire
            order_id = context.get('order_id', f"TEMP-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            # Utilise l'outil de validation
            success, message = tools.validate_order_tool(order_id, self.knowledge_base)
            
            return {
                'status': 'validated' if success else 'failed',
                'order_id': order_id,
                'message': message,
                'validation_rules': ['quantity_check', 'product_check', 'price_check']
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _execute_check_stock(self, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie le stock en utilisant les outils"""
        try:
            if not self.knowledge_base:
                return {'status': 'error', 'error': 'Knowledge base not available'}
            
            # Récupère les informations du produit et de la quantité
            product_name = entities.get('produit', context.get('product_name', 'unknown'))
            quantity = entities.get('quantite', context.get('quantity', 1))
            
            # Trouve le produit dans la base de connaissances
            product_id = self.knowledge_base.find_product_by_name(product_name)
            if not product_id:
                return {
                    'status': 'product_not_found',
                    'product_name': product_name,
                    'message': f'Produit {product_name} non trouvé'
                }
            
            # Utilise l'outil de vérification de stock
            success, message = tools.check_stock_tool(product_id, quantity, self.knowledge_base)
            
            if success:
                # Récupère les détails du produit pour plus d'informations
                product_details = self.knowledge_base.get_product_details(product_id)
                current_stock = int(product_details.get('hasStock', 0))
                
                return {
                    'status': 'available',
                    'product_id': product_id,
                    'product_name': product_name,
                    'available_quantity': current_stock,
                    'reserved_quantity': quantity,
                    'message': message
                }
            else:
                return {
                    'status': 'insufficient',
                    'product_id': product_id,
                    'product_name': product_name,
                    'message': message
                }
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _execute_calculate_price(self, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le prix en utilisant les outils"""
        try:
            if not self.knowledge_base:
                return {'status': 'error', 'error': 'Knowledge base not available'}
            
            # Récupère les informations du produit et de la quantité
            product_name = entities.get('produit', context.get('product_name', 'unknown'))
            quantity = entities.get('quantite', context.get('quantity', 1))
            
            # Trouve le produit dans la base de connaissances
            product_id = self.knowledge_base.find_product_by_name(product_name)
            if not product_id:
                return {
                    'status': 'product_not_found',
                    'product_name': product_name,
                    'message': f'Produit {product_name} non trouvé'
                }
            
            # Récupère les détails du produit
            product_details = self.knowledge_base.get_product_details(product_id)
            unit_price = float(product_details.get('hasPrice', 0))
            total_price = unit_price * quantity
            
            return {
                'status': 'calculated',
                'product_id': product_id,
                'product_name': product_name,
                'unit_price': unit_price,
                'quantity': quantity,
                'total_price': total_price,
                'currency': 'EUR'
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _execute_check_express_availability(self, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie la disponibilité de la livraison express"""
        # Simulation pour l'instant - pourrait utiliser un vrai service de livraison
        return {
            'status': 'available',
            'delivery_time': '24h',
            'zones': ['France', 'Belgique', 'Suisse'],
            'message': 'Livraison express disponible'
        }
    
    def _execute_calculate_express_cost(self, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule le coût de la livraison express"""
        # Simulation pour l'instant - pourrait utiliser un vrai service de livraison
        return {
            'express_cost': 15.00,
            'currency': 'EUR',
            'delivery_time': '24h',
            'message': 'Coût de livraison express calculé'
        }
    
    def _execute_validate_payment_method(self, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Valide la méthode de paiement"""
        # Simulation pour l'instant - pourrait utiliser un vrai service de paiement
        return {
            'status': 'valid',
            'accepted_methods': ['card', 'paypal', 'bank_transfer'],
            'security_level': 'high',
            'message': 'Méthodes de paiement validées'
        }
    
    def _execute_apply_security_checks(self, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Applique les vérifications de sécurité"""
        # Simulation pour l'instant - pourrait utiliser un vrai service de sécurité
        return {
            'status': 'secure',
            'checks_passed': ['fraud_detection', 'amount_validation', 'user_verification'],
            'risk_level': 'low',
            'message': 'Vérifications de sécurité passées'
        }
    
    def _execute_check_stock_level(self, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Vérifie le niveau de stock"""
        try:
            if not self.knowledge_base:
                return {'status': 'error', 'error': 'Knowledge base not available'}
            
            # Récupère les informations du produit
            product_name = entities.get('produit', context.get('product_name', 'unknown'))
            product_id = self.knowledge_base.find_product_by_name(product_name)
            
            if not product_id:
                return {
                    'status': 'product_not_found',
                    'product_name': product_name,
                    'message': f'Produit {product_name} non trouvé'
                }
            
            # Récupère les détails du produit
            product_details = self.knowledge_base.get_product_details(product_id)
            current_stock = int(product_details.get('hasStock', 0))
            threshold = 10  # Seuil configurable
            
            return {
                'status': 'sufficient' if current_stock > threshold else 'low',
                'product_id': product_id,
                'product_name': product_name,
                'current_level': current_stock,
                'threshold': threshold,
                'reorder_point': threshold // 2,
                'message': f'Niveau de stock: {current_stock} unités'
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _execute_send_alert_if_low(self, context: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Envoie une alerte si le stock est bas"""
        # Simulation pour l'instant - pourrait utiliser un vrai service de notification
        return {
            'status': 'alert_sent',
            'recipients': ['inventory@company.com'],
            'message': 'Alerte de stock bas envoyée',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques complètes du moteur"""
        return {
            'rule_engine': self.pyke_engine.get_rule_statistics(),
            'business_rules': {
                'total': len(self.business_rules),
                'enabled': len([r for r in self.business_rules if r.enabled]),
                'categories': self._get_rule_categories(),
                'recent_activity': self._get_recent_activity()
            }
        }
    
    def _get_rule_categories(self) -> Dict[str, int]:
        """Groupe les règles métier par catégorie"""
        categories = {}
        for rule in self.business_rules:
            categories[rule.category] = categories.get(rule.category, 0) + 1
        return categories
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Retourne l'activité récente"""
        recent_results = self.pyke_engine.inference_results[-10:]  # 10 derniers résultats
        return [
            {
                'rule': result['rule_name'],
                'confidence': result['confidence'],
                'timestamp': result['timestamp'].isoformat()
            }
            for result in recent_results
        ]
    
    def export_rules(self, format: str = 'json') -> str:
        """Exporte les règles dans différents formats"""
        if format == 'json':
            rules_data = []
            for rule in self.business_rules:
                rules_data.append({
                    'name': rule.name,
                    'description': rule.description,
                    'conditions': rule.conditions,
                    'actions': rule.actions,
                    'priority': rule.priority,
                    'category': rule.category,
                    'enabled': rule.enabled,
                    'created_at': rule.created_at.isoformat()
                })
            return json.dumps(rules_data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Format non supporté: {format}")
    
    def import_rules(self, rules_data: str, format: str = 'json'):
        """Importe des règles depuis différents formats"""
        if format == 'json':
            rules = json.loads(rules_data)
            for rule_data in rules:
                rule = BusinessRule(
                    name=rule_data['name'],
                    description=rule_data['description'],
                    conditions=rule_data['conditions'],
                    actions=rule_data['actions'],
                    priority=rule_data['priority'],
                    category=rule_data['category'],
                    enabled=rule_data.get('enabled', True),
                    created_at=datetime.fromisoformat(rule_data['created_at'])
                )
                self.add_business_rule(rule)
        else:
            raise ValueError(f"Format non supporté: {format}")


# Instance globale du moteur de règles
rule_engine = AdvancedRuleEngine()


if __name__ == "__main__":
    # Test du moteur de règles
    logging.basicConfig(level=logging.INFO)
    
    # Test d'une requête
    query = "Je veux commander 3 produits avec livraison express"
    result = rule_engine.process_query(query)
    
    print("=== Test du Moteur de Règles ===")
    print(f"Requête: {query}")
    print(f"Intention détectée: {result['intent']}")
    print(f"Entités extraites: {result['entities']}")
    print(f"Confiance: {result['confidence']:.2f}")
    print(f"Actions exécutées: {len(result['executed_actions'])}")
    
    # Statistiques
    stats = rule_engine.get_statistics()
    print(f"\nStatistiques:")
    print(f"- Règles totales: {stats['business_rules']['total']}")
    print(f"- Règles activées: {stats['business_rules']['enabled']}")
    print(f"- Catégories: {stats['business_rules']['categories']}") 