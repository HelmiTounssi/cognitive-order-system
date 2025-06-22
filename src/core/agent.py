"""
Module Agent - Logique principale avec vrai LLM
Orchestre les interactions entre la base de connaissances, la base vectorielle et les outils
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from src.core.knowledge_base import KnowledgeBase
from src.rag.vector_store import VectorStore
from src.core.rule_engine import AdvancedRuleEngine
from src.mcp.mcp_client import create_mcp_interface
from src.mcp import tools


class CognitiveOrderAgent:
    def __init__(self, knowledge_base: KnowledgeBase, vector_store: VectorStore, 
                 llm_interface=None, use_mcp: bool = False, mcp_server_url: str = "ws://localhost:8001"):
        """
        Initialise l'agent cognitif
        
        Args:
            knowledge_base: Instance de la base de connaissances
            vector_store: Instance de la base vectorielle
            llm_interface: Interface LLM (optionnel)
            use_mcp: Utilise le serveur MCP pour les outils
            mcp_server_url: URL du serveur MCP
        """
        self.kb = knowledge_base
        self.vector_store = vector_store
        self.llm_interface = llm_interface
        self.use_mcp = use_mcp
        self.mcp_server_url = mcp_server_url
        
        # Initialisation du client MCP si nécessaire
        self.mcp_interface = None
        if self.use_mcp:
            try:
                self.mcp_interface = create_mcp_interface(mcp_server_url)
                self.mcp_interface.connect()
                print(f"✅ Connecté au serveur MCP: {mcp_server_url}")
            except Exception as e:
                print(f"❌ Erreur de connexion au serveur MCP: {e}")
                print("🔄 Utilisation des outils locaux en fallback")
                self.use_mcp = False
        
        # Initialisation du moteur de règles avancé avec la base de connaissances
        self.rule_engine = AdvancedRuleEngine(knowledge_base=knowledge_base)
        
        # Patterns améliorés pour l'extraction d'intentions (fallback si pas de LLM)
        self.intent_patterns = {
            'create_order': [
                r'créer.*commande',
                r'nouvelle.*commande',
                r'passer.*commande',
                r'commander',
                r'faire.*commande',
                r'placer.*commande'
            ],
            'validate_order': [
                r'valider.*commande',
                r'confirmer.*commande',
                r'traiter.*commande',
                r'approuver.*commande'
            ],
            'recommend_products': [
                r'recommander',
                r'suggérer',
                r'similaire',
                r'accessoire',
                r'chercher',
                r'proposer',
                r'conseiller'
            ],
            'check_status': [
                r'statut',
                r'état',
                r'historique',
                r'vérifier.*commande',
                r'où.*en.*est'
            ],
            'list_orders': [
                r'liste.*commandes',
                r'voir.*commandes',
                r'afficher.*commandes',
                r'toutes.*commandes',
                r'commandes.*disponibles',
                r'mes.*commandes'
            ],
            'process_payment': [
                r'paiement',
                r'payer',
                r'facturer',
                r'régler',
                r'effectuer.*paiement'
            ],
            'add_client': [
                r'ajouter.*client',
                r'nouveau.*client',
                r'créer.*client',
                r'enregistrer.*client',
                r'inscrire.*client'
            ],
            'list_clients': [
                r'lister.*clients',
                r'voir.*clients',
                r'afficher.*clients',
                r'liste.*clients',
                r'tous.*clients'
            ],
            'introspect_ontology': [
                r'introspection',
                r'structure.*ontologie',
                r'analyser.*ontologie',
                r'voir.*structure',
                r'explorer.*ontologie'
            ],
            'extend_ontology': [
                r'ajouter.*classe',
                r'créer.*classe',
                r'nouvelle.*classe',
                r'étendre.*ontologie'
            ],
            'create_instance': [
                r'créer.*instance',
                r'nouvelle.*instance',
                r'ajouter.*instance'
            ],
            'add_behavior_class': [
                r'ajouter.*comportement',
                r'créer.*comportement',
                r'classe.*comportement',
                r'méthodes.*classe'
            ],
            'add_state_machine': [
                r'ajouter.*machine.*états',
                r'créer.*machine.*états',
                r'états.*transitions',
                r'automate.*états'
            ],
            'execute_behavior': [
                r'exécuter.*méthode',
                r'appeler.*méthode',
                r'invoquer.*comportement',
                r'passer.*commande',
                r'payer',
                r'changer.*état'
            ],
            'create_semantic_proxy': [
                r'créer.*proxy',
                r'nouveau.*proxy',
                r'proxy.*sémantique',
                r'proxy.*classe'
            ],
            'execute_reflection': [
                r'exécuter.*réflexion',
                r'méthode.*réflexion',
                r'appel.*dynamique',
                r'invocation.*réflexive'
            ],
            'reflect_class': [
                r'réflexion.*classe',
                r'analyser.*classe',
                r'structure.*classe',
                r'inspecter.*classe'
            ],
            'instantiate_reflection': [
                r'instancier.*réflexion',
                r'créer.*instance.*réflexion',
                r'nouveau.*objet.*réflexion'
            ],
            'query_ontology': [
                r'requêter.*ontologie',
                r'interroger.*ontologie',
                r'chercher.*dans.*ontologie'
            ]
        }
        
        # Patterns améliorés pour l'extraction d'entités
        self.entity_patterns = {
            'client_name': [
                r'pour\s+([a-zA-ZÀ-ÿ\s]+)',
                r'client\s+([a-zA-ZÀ-ÿ\s]+)',
                r'nom[ée]?\s+([a-zA-ZÀ-ÿ\s]+)',
                r'(?:client|nouveau)\s+([a-zA-ZÀ-ÿ\s]+)',
                r'([a-zA-ZÀ-ÿ\s]+)\s+veut\s+commander',
                r'commande\s+pour\s+([a-zA-ZÀ-ÿ\s]+)'
            ],
            'order_id': [
                r'([A-Z]-\d+)',
                r'commande\s+([A-Z]-\d+)',
                r'numéro\s+([A-Z]-\d+)',
                r'([A-Z]-\d+)\s*$'
            ],
            'amount': [
                r'(\d+(?:[.,]\d+)?)\s*€',
                r'montant\s+de\s+(\d+(?:[.,]\d+)?)',
                r'(\d+(?:[.,]\d+)?)\s*euros?',
                r'prix\s+(\d+(?:[.,]\d+)?)',
                r'coût\s+(\d+(?:[.,]\d+)?)'
            ],
            'email': [
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'courriel[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ],
            'phone': [
                r'(\d{2}[.\s-]?\d{2}[.\s-]?\d{2}[.\s-]?\d{2}[.\s-]?\d{2})',
                r'téléphone[:\s]*(\d{2}[.\s-]?\d{2}[.\s-]?\d{2}[.\s-]?\d{2}[.\s-]?\d{2})',
                r'portable[:\s]*(\d{2}[.\s-]?\d{2}[.\s-]?\d{2}[.\s-]?\d{2}[.\s-]?\d{2})'
            ],
            'product_name': [
                r'([a-zA-ZÀ-ÿ\s]+)\s+(?:avec|pour|de)\s+\d+',
                r'(\d+)\s+(?:unités?|pièces?)\s+de\s+([a-zA-ZÀ-ÿ\s]+)',
                r'([a-zA-ZÀ-ÿ\s]+)\s+(?:ordinateur|souris|clavier|écran)',
                r'produit\s+([a-zA-ZÀ-ÿ\s]+)'
            ],
            'quantity': [
                r'(\d+)\s+(?:unités?|pièces?|exemplaires?)',
                r'quantité[:\s]*(\d+)',
                r'nombre[:\s]*(\d+)'
            ],
            'query_text': [
                r'recommande\s+(.+)',
                r'cherche\s+(.+)',
                r'suggère\s+(.+)',
                r'propose\s+(.+)',
                r'conseille\s+(.+)'
            ]
        }
    
    def run_agent(self, user_query: str) -> str:
        """
        Point d'entrée principal de l'agent
        
        Args:
            user_query: Requête utilisateur en langage naturel
        
        Returns:
            str: Réponse de l'agent
        """
        try:
            print(f"\n🤖 Agent: Analyse de la requête: '{user_query}'")
            
            # Étape 1: Traitement par le moteur de règles avancé
            print("🔧 Application du moteur de règles...")
            rule_result = self.rule_engine.process_query(user_query)
            
            if rule_result['inference_results']:
                print(f"✅ Règles appliquées: {len(rule_result['inference_results'])}")
                print(f"🎯 Intention détectée par règles: {rule_result['intent']}")
                print(f"📊 Confiance des règles: {rule_result['confidence']:.2f}")
                
                # Si les règles ont une confiance élevée, on les utilise
                if rule_result['confidence'] > 0.7:
                    return self._process_rule_based_response(rule_result)
            
            # Étape 2: Extraction de l'intention et des paramètres (fallback)
            if self.llm_interface:
                # Utilise le vrai LLM
                intent, params, confidence = self.llm_interface.extract_intent_and_parameters(user_query)
                print(f"🎯 LLM - Intention détectée: {intent} (confiance: {confidence:.2f})")
            else:
                # Fallback vers la logique simulée
                intent = self._extract_intent(user_query)
                params = self._extract_parameters(user_query, intent)
                confidence = 0.8  # Confiance simulée
                print(f"🎯 Simulé - Intention détectée: {intent}")
            
            print(f"📋 Paramètres extraits: {params}")
            
            # Étape 3: Exécution de la logique métier
            response = self._execute_intent(intent, params)
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Erreur lors du traitement: {e}"
            print(error_msg)
            return error_msg
    
    def _process_rule_based_response(self, rule_result: Dict) -> str:
        """Traite la réponse basée sur les règles du moteur"""
        try:
            executed_actions = rule_result['executed_actions']
            entities = rule_result['entities']
            
            response_parts = []
            response_parts.append("🤖 **Réponse basée sur les règles métier:**")
            
            # Affichage des actions exécutées
            for action_info in executed_actions:
                action = action_info['action']
                result = action_info['result']
                rule = action_info['rule']
                
                response_parts.append(f"\n📋 **Action:** {action}")
                response_parts.append(f"🔧 **Règle:** {rule}")
                
                # Formatage des résultats selon l'action
                if action == 'validate_order':
                    response_parts.append(f"✅ Commande validée: {result.get('order_id', 'N/A')}")
                elif action == 'check_stock':
                    response_parts.append(f"📦 Stock disponible: {result.get('available_quantity', 0)} unités")
                elif action == 'calculate_price':
                    response_parts.append(f"💰 Prix total: {result.get('total_price', 0)} {result.get('currency', 'EUR')}")
                elif action == 'check_express_availability':
                    response_parts.append(f"🚚 Livraison express: {result.get('status', 'N/A')}")
                elif action == 'calculate_express_cost':
                    response_parts.append(f"💳 Coût express: {result.get('express_cost', 0)} {result.get('currency', 'EUR')}")
                elif action == 'validate_payment_method':
                    response_parts.append(f"💳 Paiement: {result.get('status', 'N/A')}")
                else:
                    response_parts.append(f"📊 Résultat: {result}")
            
            # Affichage des entités extraites
            if entities:
                response_parts.append(f"\n🔍 **Entités détectées:**")
                for key, value in entities.items():
                    if value is not None:
                        response_parts.append(f"  - {key}: {value}")
            
            # Affichage de la confiance
            response_parts.append(f"\n🎯 **Confiance:** {rule_result['confidence']:.2f}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            return f"❌ Erreur lors du traitement des règles: {e}"
    
    def _extract_intent(self, query: str) -> str:
        """
        Extrait l'intention de la requête utilisateur (fallback)
        Simule le parsing d'un LLM avec des expressions régulières
        """
        query_lower = query.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        # Intention par défaut si aucune correspondance
        return "unknown"
    
    def _extract_parameters(self, query: str, intent: str) -> Dict:
        """
        Extrait les paramètres de la requête en utilisant la réflexion
        Utilise des handlers d'intention automatiques au lieu de conditions hardcodées
        """
        try:
            # Utilise la réflexion pour trouver le handler d'extraction
            handler_method_name = f"_extract_params_{intent}"
            
            if hasattr(self, handler_method_name):
                # Appelle le handler spécifique via réflexion
                handler_method = getattr(self, handler_method_name)
                params = handler_method(query)
                print(f"🔄 Extraction réflexive pour '{intent}': {params}")
                return params
            else:
                # Handler générique si aucun handler spécifique n'existe
                print(f"⚠️ Aucun handler spécifique pour '{intent}', utilisation du handler générique")
                return self._extract_params_generic(query, intent)
                
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction réflexive: {e}")
            return self._extract_params_generic(query, intent)
    
    def _extract_params_generic(self, query: str, intent: str) -> Dict:
        """
        Handler générique d'extraction de paramètres amélioré
        Utilise des patterns robustes et extraction LLM de fallback
        """
        params = {}
        query_lower = query.lower()
        
        # Nettoyage de la requête
        query_clean = re.sub(r'\s+', ' ', query_lower.strip())
        
        # Extraction avec les patterns améliorés
        for param_name, patterns in self.entity_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_clean, re.IGNORECASE)
                if match:
                    # Nettoyage de la valeur extraite
                    value = match.group(1).strip()
                    if value and len(value) > 1:  # Évite les valeurs trop courtes
                        params[param_name] = value
                        break
        
        # Extraction spéciale pour les produits avec patterns améliorés
        if 'product' in intent or 'order' in intent:
            products = self._extract_products_from_query(query)
            if products:
                params['products'] = products
        
        # Si pas assez de paramètres extraits, essayer l'extraction LLM
        if len(params) < 2 and self.llm_interface:
            try:
                llm_params = self._extract_with_llm_fallback(query, intent)
                # Fusion des paramètres (LLM en priorité)
                for key, value in llm_params.items():
                    if value:  # Ne pas écraser avec des valeurs vides
                        params[key] = value
                print(f"🤖 LLM fallback extrait: {llm_params}")
            except Exception as e:
                print(f"⚠️ Erreur extraction LLM fallback: {e}")
        
        return params
    
    def _extract_with_llm_fallback(self, query: str, intent: str) -> Dict:
        """
        Extraction de fallback avec LLM pour les cas difficiles
        """
        if not self.llm_interface:
            return {}
        
        # Prompt spécialisé pour l'extraction d'entités
        prompt = f"""
        Extrait les entités importantes de cette requête pour l'intention '{intent}'.
        
        Requête: "{query}"
        
        Retourne uniquement un JSON avec les entités trouvées:
        {{
            "client_name": "nom du client si trouvé",
            "order_id": "ID de commande si trouvé (format A-123)",
            "amount": "montant si trouvé (nombre)",
            "email": "email si trouvé",
            "phone": "téléphone si trouvé",
            "product_name": "nom du produit si trouvé",
            "quantity": "quantité si trouvée (nombre)",
            "query_text": "texte de recherche si trouvé"
        }}
        
        Si une entité n'est pas trouvée, utilise null. Retourne uniquement le JSON.
        """
        
        try:
            response = self.llm_interface.generate_response(prompt)
            # Nettoyage de la réponse pour extraire le JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                llm_params = json.loads(json_str)
                # Nettoyage des valeurs null/vides
                return {k: v for k, v in llm_params.items() if v and v != "null"}
            return {}
        except Exception as e:
            print(f"❌ Erreur parsing JSON LLM: {e}")
            return {}
    
    def _extract_products_from_query(self, query: str) -> List[Dict]:
        """Extrait les produits et quantités d'une requête avec patterns améliorés"""
        products = []
        query_lower = query.lower()
        
        # Patterns améliorés pour l'extraction de produits
        patterns = [
            # "X unités de Y"
            (r'(\d+)\s+(?:unités?|pièces?|exemplaires?)\s+(?:de\s+)?([a-zA-ZÀ-ÿ\s]+)', 1, 2),
            # "Y avec X unités"
            (r'([a-zA-ZÀ-ÿ\s]+)\s+(?:avec\s+)?(\d+)\s+(?:unités?|pièces?|exemplaires?)', 2, 1),
            # "X Y" (quantité + produit)
            (r'(\d+)\s+([a-zA-ZÀ-ÿ\s]{3,})', 1, 2),
            # "Y X" (produit + quantité)
            (r'([a-zA-ZÀ-ÿ\s]{3,})\s+(\d+)', 2, 1),
            # "commander X Y"
            (r'commander\s+(\d+)\s+([a-zA-ZÀ-ÿ\s]+)', 1, 2),
            # "veux X Y"
            (r'veux\s+(\d+)\s+([a-zA-ZÀ-ÿ\s]+)', 1, 2)
        ]
        
        for pattern, qty_group, prod_group in patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                try:
                    quantity = int(match[qty_group - 1])
                    product_name = match[prod_group - 1].strip()
                    
                    # Nettoyage du nom du produit
                    product_name = re.sub(r'\b(?:unités?|pièces?|exemplaires?|de|avec|pour)\b', '', product_name).strip()
                    
                    if product_name and len(product_name) > 2 and quantity > 0:
                        # Vérification si le produit n'est pas déjà dans la liste
                        existing = next((p for p in products if p['product_name'].lower() == product_name.lower()), None)
                        if existing:
                            existing['quantity'] += quantity
                        else:
                            products.append({
                                'product_name': product_name,
                                'quantity': quantity
                            })
                except (ValueError, IndexError):
                    continue
        
        # Si pas de produits trouvés avec regex, essayer LLM
        if not products and self.llm_interface:
            try:
                llm_products = self._extract_products_with_llm(query)
                products.extend(llm_products)
            except Exception as e:
                print(f"⚠️ Erreur extraction produits LLM: {e}")
        
        return products
    
    def _extract_products_with_llm(self, query: str) -> List[Dict]:
        """Extraction de produits avec LLM de fallback"""
        if not self.llm_interface:
            return []
        
        prompt = f"""
        Extrait les produits et quantités de cette requête de commande.
        
        Requête: "{query}"
        
        Retourne uniquement un JSON avec la liste des produits:
        [
            {{"product_name": "nom du produit", "quantity": nombre}},
            ...
        ]
        
        Si aucun produit n'est trouvé, retourne []. Retourne uniquement le JSON.
        """
        
        try:
            response = self.llm_interface.generate_response(prompt)
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            return []
        except Exception as e:
            print(f"❌ Erreur parsing produits JSON LLM: {e}")
            return []
    
    # Handlers spécifiques d'extraction de paramètres (réflexion automatique)
    
    def _extract_params_create_order(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres de création de commande"""
        params = self._extract_params_generic(query, "create_order")
        
        # Logique spécifique pour create_order
        query_lower = query.lower()
        
        # Vérification si paiement immédiat
        if any(word in query_lower for word in ['payer', 'paiement', 'traiter']):
            params['immediate_payment'] = True
        
        return params
    
    def _extract_params_recommend_products(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres de recommandation"""
        params = self._extract_params_generic(query, "recommend_products")
        query_lower = query.lower()
        
        # Logique spécifique pour recommend_products
        if 'similaire' in query_lower:
            similar_match = re.search(r'similaire\s+à\s+([a-zA-Z\s]+)', query_lower)
            if similar_match:
                params['reference_product'] = similar_match.group(1).strip()
        
        if 'accessoire' in query_lower:
            params['query_text'] = "accessoire pour ordinateur"
        elif 'gaming' in query_lower:
            params['query_text'] = "produit gaming"
        else:
            # Extraction du texte de recherche en supprimant les mots de liaison
            stop_words = ['recommande', 'moi', 'des', 'les', 'un', 'une', 'pour', 'avec', 'et', 'ou']
            words = query_lower.split()
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
            if keywords:
                params['query_text'] = ' '.join(keywords)
            else:
                # Fallback: prend les derniers mots significatifs
                search_words = re.findall(r'\b[a-zA-Z]{3,}\b', query_lower)
                if len(search_words) > 0:
                    params['query_text'] = ' '.join(search_words[-3:])
        
        return params
    
    def _extract_params_add_client(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres d'ajout de client"""
        return self._extract_params_generic(query, "add_client")
    
    def _extract_params_validate_order(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres de validation de commande"""
        return self._extract_params_generic(query, "validate_order")
    
    def _extract_params_check_status(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres de vérification de statut"""
        return self._extract_params_generic(query, "check_status")
    
    def _extract_params_process_payment(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres de traitement de paiement"""
        return self._extract_params_generic(query, "process_payment")
    
    def _extract_params_list_clients(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres de liste de clients"""
        return {}  # Pas de paramètres pour lister les clients
    
    def _extract_params_list_orders(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres de liste de commandes"""
        return {}  # Pas de paramètres pour lister les commandes
    
    def _extract_params_introspect_ontology(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres d'introspection"""
        return {}
    
    def _extract_params_extend_ontology(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres d'extension d'ontologie"""
        params = {}
        query_lower = query.lower()
        
        # Extraction du nom de classe
        class_match = re.search(r'classe\s+([a-zA-Z]+)', query_lower)
        if class_match:
            params['class_name'] = class_match.group(1)
        
        # Extraction des propriétés (simplifié)
        properties_match = re.search(r'propriétés?\s+(.+)', query_lower)
        if properties_match:
            # Logique simplifiée pour extraire les propriétés
            props_text = properties_match.group(1)
            # Ici on pourrait parser plus intelligemment les propriétés
            params['properties'] = [{'name': 'hasName', 'type': 'string', 'label': 'Nom'}]
        
        return params
    
    def _extract_params_create_instance(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres de création d'instance"""
        params = {}
        query_lower = query.lower()
        
        # Extraction du nom de classe
        class_match = re.search(r'instance\s+de\s+([a-zA-Z]+)', query_lower)
        if class_match:
            params['class_name'] = class_match.group(1)
        
        return params
    
    def _extract_params_query_ontology(self, query: str) -> Dict:
        """Handler spécifique pour l'extraction des paramètres de requête d'ontologie"""
        params = {}
        query_lower = query.lower()
        
        if 'classes' in query_lower:
            params['query_type'] = 'classes'
        elif 'propriétés' in query_lower or 'properties' in query_lower:
            params['query_type'] = 'properties'
        elif 'instances' in query_lower:
            params['query_type'] = 'instances'
        else:
            params['query_type'] = 'structure'
        
        return params
    
    def _execute_intent(self, intent: str, params: Dict) -> str:
        """
        Exécute la logique métier basée sur l'intention en utilisant la réflexion
        Utilise des handlers d'exécution automatiques au lieu de conditions hardcodées
        """
        try:
            # Si MCP est disponible, utilise-le en priorité
            if self.use_mcp and self.mcp_interface:
                print(f"🌐 Utilisation du serveur MCP pour l'intention '{intent}'")
                return self._execute_intent_via_mcp(intent, params)
            
            # Sinon, utilise la logique locale
            # Utilise la réflexion pour trouver le handler d'exécution
            handler_method_name = f"_handle_{intent}"
            
            if hasattr(self, handler_method_name):
                # Appelle le handler spécifique via réflexion
                handler_method = getattr(self, handler_method_name)
                result = handler_method(params)
                print(f"🔄 Exécution réflexive pour '{intent}'")
                return result
            else:
                # Handler générique si aucun handler spécifique n'existe
                print(f"⚠️ Aucun handler spécifique pour '{intent}', utilisation du handler générique")
                return self._handle_generic(params, intent)
                
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution réflexive: {e}")
            return f"❌ Erreur lors de l'exécution de l'intention '{intent}': {e}"
    
    def _handle_generic(self, params: Dict, intent: str) -> str:
        """
        Handler générique d'exécution d'intention
        Utilisé quand aucun handler spécifique n'existe
        """
        return f"❌ Intention '{intent}' non reconnue. Veuillez reformuler votre demande."
    
    def _handle_create_order(self, params: Dict) -> str:
        """
        Gère la création d'une commande
        Simule l'inférence sur l'ontologie pour le processus de commande
        """
        try:
            # Étape 1: Recherche ou création du client
            client_name = params.get('client_name')
            if not client_name:
                return "❌ Nom du client manquant dans la requête."
            
            client_id = self.kb.find_client_by_name(client_name)
            if not client_id:
                # Inférence: créer un nouveau client
                print(f"🆕 Client '{client_name}' non trouvé, création d'un nouveau client")
                client_id = self.kb.add_client(f"client_{client_name.lower().replace(' ', '_')}", 
                                             client_name, f"{client_name.lower().replace(' ', '.')}@email.com")
            
            # Étape 2: Validation des produits
            products = params.get('products', [])
            if not products:
                return "❌ Aucun produit spécifié dans la commande."
            
            validated_items = []
            total_amount = 0.0
            
            for product_info in products:
                product_name = product_info['product_name']
                quantity = product_info['quantity']
                
                # Recherche du produit dans la base de connaissances
                product_id = self.kb.find_product_by_name(product_name)
                if not product_id:
                    return f"❌ Produit '{product_name}' non trouvé dans le catalogue."
                
                # Vérification du stock
                success, message = tools.check_stock_tool(product_id, quantity, self.kb)
                if not success:
                    # Utilise le LLM pour une explication d'erreur intelligente
                    if self.llm_interface:
                        error_explanation = self.llm_interface.get_error_explanation(
                            "stock_insufficient", 
                            f"Produit: {product_name}, Quantité demandée: {quantity}"
                        )
                        return f"❌ {message}\n\n{error_explanation}"
                    else:
                        return f"❌ {message}"
                
                # Récupération des détails pour le calcul du montant
                product_details = self.kb.get_product_details(product_id)
                price = float(product_details.get('hasPrice', 0))
                item_total = price * quantity
                total_amount += item_total
                
                validated_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'price': price,
                    'total': item_total
                })
            
            # Étape 3: Création de la commande
            order_id = tools.create_order_tool(client_id, validated_items, self.kb)
            if not order_id:
                return "❌ Erreur lors de la création de la commande."
            
            # Étape 4: Traitement du paiement si demandé
            if params.get('immediate_payment', False):
                print("💳 Traitement du paiement immédiat...")
                payment_success, payment_message = tools.process_payment_tool(order_id, total_amount, self.kb)
                
                if payment_success:
                    return f"✅ Commande {order_id} créée et payée avec succès!\nMontant total: {total_amount:.2f}€"
                else:
                    return f"⚠️ Commande {order_id} créée mais échec du paiement: {payment_message}"
            
            return f"✅ Commande {order_id} créée avec succès!\nMontant total: {total_amount:.2f}€\nStatut: En attente de paiement"
            
        except Exception as e:
            return f"❌ Erreur lors de la création de la commande: {e}"
    
    def _handle_validate_order(self, params: Dict) -> str:
        """
        Gère la validation d'une commande
        Simule l'inférence conditionnelle sur l'ontologie
        """
        try:
            order_id = params.get('order_id')
            if not order_id:
                return "❌ ID de commande manquant dans la requête."
            
            # Récupération des détails de la commande
            order_details = self.kb.get_order_details(order_id)
            if not order_details:
                return f"❌ Commande {order_id} non trouvée."
            
            current_status = order_details.get('hasStatus', '')
            
            # Inférence: vérification du statut actuel
            if current_status != "en_attente":
                return f"⚠️ Commande {order_id} déjà traitée (statut: {current_status})"
            
            # Exécution de la validation
            success, message = tools.validate_order_tool(order_id, self.kb)
            
            if success:
                # Inférence: si validation réussie, proposer le paiement
                amount = float(order_details.get('hasAmount', 0))
                payment_success, payment_message = tools.process_payment_tool(order_id, amount, self.kb)
                
                if payment_success:
                    return f"✅ Commande {order_id} validée et payée avec succès!\n{message}"
                else:
                    return f"⚠️ Commande {order_id} validée mais échec du paiement: {payment_message}"
            else:
                # Inférence: si échec de stock, proposer des alternatives
                if "stock insuffisant" in message.lower():
                    recommendations = tools.recommend_products_tool("produit similaire", self.vector_store, self.kb, 3)
                    if recommendations:
                        alt_products = ", ".join([rec['name'] for rec in recommendations])
                        return f"❌ {message}\n\n💡 Alternatives suggérées: {alt_products}"
                
                return f"❌ {message}"
            
        except Exception as e:
            return f"❌ Erreur lors de la validation: {e}"
    
    def _handle_recommend_products(self, params: Dict) -> str:
        """
        Gère les recommandations de produits
        Utilise la recherche vectorielle pour la similarité
        """
        try:
            query_text = params.get('query_text', '')
            reference_product = params.get('reference_product', '')
            
            # Nettoie le query_text pour extraire les mots-clés pertinents
            if query_text:
                # Supprime les mots de liaison et garde les mots-clés
                stop_words = ['recommande', 'moi', 'des', 'les', 'un', 'une', 'pour', 'avec', 'et', 'ou', 'je', 'cherche', 'veux', 'voudrais']
                words = query_text.lower().split()
                keywords = [word for word in words if word not in stop_words and len(word) > 2]
                clean_query = ' '.join(keywords)
            else:
                clean_query = ''
            
            # Logique de recherche améliorée
            search_queries = []
            
            if reference_product:
                search_queries.append(f"produit similaire à {reference_product}")
            
            if clean_query:
                search_queries.append(clean_query)
                # Ajoute des variantes pour améliorer les chances de trouver des résultats
                if 'accessoire' in clean_query or 'accessoires' in clean_query:
                    search_queries.append("accessoire ordinateur")
                    search_queries.append("hub usb")
                if 'gaming' in clean_query:
                    search_queries.append("produit gaming")
                    search_queries.append("souris gaming")
                if 'laptop' in clean_query or 'portable' in clean_query:
                    search_queries.append("ordinateur portable")
                    search_queries.append("laptop")
            
            # Si aucune requête spécifique, utilise une recherche générique
            if not search_queries:
                search_queries = ["produit informatique", "accessoire ordinateur"]
            
            recommendations = []
            best_query = ""
            
            # Essaie différentes requêtes jusqu'à trouver des résultats
            for query in search_queries:
                print(f"🔍 Tentative de recherche avec: '{query}'")
                temp_recommendations = tools.recommend_products_tool(
                    query, self.vector_store, self.kb, 3
                )
                if temp_recommendations:
                    recommendations = temp_recommendations
                    best_query = query
                    break
            
            if not recommendations:
                # Fallback: récupère tous les produits disponibles
                print("🔍 Aucune recommandation trouvée, affichage de tous les produits disponibles")
                all_products = []
                for product_uri in self.kb.get_instances_of_class("http://example.org/ontology/Product"):
                    product_id = product_uri.split('/')[-1]
                    product_details = self.kb.get_product_details(product_id)
                    if product_details:
                        all_products.append({
                            'name': product_details.get('hasName', ''),
                            'price': product_details.get('hasPrice', 0),
                            'description': product_details.get('hasDescription', ''),
                            'stock': product_details.get('hasStock', 0),
                            'similarity_score': 0.5  # Score par défaut
                        })
                
                if all_products:
                    response = "🎯 Voici tous nos produits disponibles:\n\n"
                    for i, product in enumerate(all_products, 1):
                        response += f"{i}. **{product['name']}** - {product['price']}€\n"
                        response += f"   {product['description']}\n"
                        response += f"   Stock: {product['stock']} unités\n\n"
                    return response
                else:
                    return "❌ Aucun produit disponible dans le catalogue."
            
            # Si on a un LLM, utilise-le pour générer des recommandations intelligentes
            if self.llm_interface:
                # Récupère tous les produits disponibles pour le LLM
                all_products = []
                for product_uri in self.kb.get_instances_of_class("http://example.org/ontology/Product"):
                    product_id = product_uri.split('/')[-1]
                    product_details = self.kb.get_product_details(product_id)
                    all_products.append({
                        'name': product_details.get('hasName', ''),
                        'description': product_details.get('hasDescription', ''),
                        'price': product_details.get('hasPrice', 0)
                    })
                
                # Utilise le LLM pour des recommandations plus intelligentes
                llm_recommendations = self.llm_interface.get_product_recommendations(
                    best_query or clean_query or f"produit similaire à {reference_product}", 
                    all_products
                )
                
                return f"🎯 Recommandations intelligentes:\n\n{llm_recommendations}"
            
            # Fallback vers les recommandations vectorielles
            response = f"🎯 Voici mes recommandations pour '{best_query}':\n\n"
            for i, rec in enumerate(recommendations, 1):
                response += f"{i}. **{rec['name']}** - {rec['price']}€\n"
                response += f"   {rec['description']}\n"
                response += f"   Stock: {rec['stock']} unités\n"
                response += f"   Score de similarité: {rec['similarity_score']:.2f}\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Erreur lors de la génération des recommandations: {e}"
    
    def _handle_check_status(self, params: Dict) -> str:
        """
        Gère la vérification du statut des commandes
        """
        try:
            order_id = params.get('order_id')
            client_name = params.get('client_name')
            
            if order_id:
                # Vérification du statut d'une commande spécifique
                order_details = self.kb.get_order_details(order_id)
                if not order_details:
                    return f"❌ Commande {order_id} non trouvée."
                
                response = f"📋 Statut de la commande {order_id}:\n"
                response += f"   Montant: {order_details.get('hasAmount', 'N/A')}€\n"
                response += f"   Statut: {order_details.get('hasStatus', 'N/A')}\n"
                
                return response
            
            elif client_name:
                # Historique des commandes d'un client
                client_id = self.kb.find_client_by_name(client_name)
                if not client_id:
                    return f"❌ Client '{client_name}' non trouvé."
                
                orders = tools.get_order_history_tool(client_id, self.kb)
                if not orders:
                    return f"📋 Aucune commande trouvée pour le client '{client_name}'."
                
                response = f"📋 Historique des commandes pour '{client_name}':\n\n"
                for order in orders:
                    response += f"   {order['order_id']}: {order['amount']}€ - {order['status']}\n"
                
                return response
            
            else:
                return "❌ Veuillez spécifier un ID de commande ou un nom de client."
            
        except Exception as e:
            return f"❌ Erreur lors de la vérification du statut: {e}"
    
    def _handle_process_payment(self, params: Dict) -> str:
        """
        Gère le traitement des paiements
        """
        try:
            # Cette fonction pourrait être étendue pour traiter des paiements spécifiques
            return "💳 Fonctionnalité de paiement en cours de développement."
            
        except Exception as e:
            return f"❌ Erreur lors du traitement du paiement: {e}"
    
    def _handle_add_client(self, params: Dict) -> str:
        """
        Gère l'ajout d'un nouveau client
        """
        try:
            client_name = params.get('client_name')
            if not client_name:
                return "❌ Nom du client manquant dans la requête."
            
            # Vérification de l'existence du client
            existing_client = self.kb.find_client_by_name(client_name)
            if existing_client:
                return f"❌ Client '{client_name}' déjà existant."
            
            # Ajout du nouveau client
            client_id = self.kb.add_client(f"client_{client_name.lower().replace(' ', '_')}", 
                                         client_name, f"{client_name.lower().replace(' ', '.')}@email.com")
            
            return f"✅ Client '{client_name}' ajouté avec succès! ID: {client_id}"
            
        except Exception as e:
            return f"❌ Erreur lors de l'ajout du client: {e}"
    
    def _handle_list_clients(self, params: Dict) -> str:
        """
        Gère la liste des clients
        """
        try:
            clients = self.kb.get_clients()
            if not clients:
                return "📋 Aucun client trouvé."
            
            response = "📋 Liste des clients:\n\n"
            for client in clients:
                response += f"   ID: {client['id']}, Nom: {client['name']}, Email: {client['email']}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Erreur lors de la récupération de la liste des clients: {e}"
    
    def _handle_introspect_ontology(self, params: Dict) -> str:
        """
        Gère l'introspection de l'ontologie
        """
        try:
            ontology_info = tools.introspect_ontology_tool(self.kb)
            
            if not ontology_info:
                return "❌ Erreur lors de l'introspection de l'ontologie."
            
            response = "🔍 Introspection de l'ontologie:\n\n"
            response += f"📊 **Classes** ({len(ontology_info.get('classes', []))}):\n"
            for class_info in ontology_info.get('classes', []):
                response += f"   - {class_info['name']}: {class_info['instances_count']} instances\n"
            
            response += f"\n📊 **Propriétés** ({len(ontology_info.get('properties', []))}):\n"
            for prop_info in ontology_info.get('properties', []):
                response += f"   - {prop_info['name']} ({prop_info['type']}): {prop_info['range']}\n"
            
            response += f"\n📊 **Namespaces** ({len(ontology_info.get('namespaces', {}))}):\n"
            for prefix, uri in ontology_info.get('namespaces', {}).items():
                response += f"   - {prefix}: {uri}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Erreur lors de l'introspection: {e}"
    
    def _handle_extend_ontology(self, params: Dict) -> str:
        """
        Gère l'extension dynamique de l'ontologie
        """
        try:
            class_name = params.get('class_name')
            properties = params.get('properties', [])
            namespace = params.get('namespace')
            
            if not class_name:
                return "❌ Nom de la classe manquant dans la requête."
            
            if not properties:
                return "❌ Aucune propriété spécifiée pour la nouvelle classe."
            
            success, message = tools.extend_ontology_tool(class_name, properties, self.kb, namespace)
            
            if success:
                return f"✅ {message}"
            else:
                return f"❌ {message}"
            
        except Exception as e:
            return f"❌ Erreur lors de l'extension de l'ontologie: {e}"
    
    def _handle_create_instance(self, params: Dict) -> str:
        """
        Gère la création dynamique d'instances
        """
        try:
            class_name = params.get('class_name')
            properties = params.get('properties', {})
            instance_id = params.get('instance_id')
            
            if not class_name:
                return "❌ Nom de la classe manquant dans la requête."
            
            if not properties:
                return "❌ Aucune propriété spécifiée pour la nouvelle instance."
            
            success, message = tools.create_instance_tool(class_name, properties, self.kb, instance_id)
            
            if success:
                return f"✅ {message}"
            else:
                return f"❌ {message}"
            
        except Exception as e:
            return f"❌ Erreur lors de la création de l'instance: {e}"
    
    def _handle_add_behavior_class(self, params: Dict) -> str:
        """
        Gère l'ajout d'une classe de comportement
        """
        try:
            class_name = params.get('class_name')
            if not class_name:
                return "❌ Nom de la classe manquant dans la requête."
            
            # Vérification de l'existence de la classe
            existing_class = self.kb.find_class_by_name(class_name)
            if existing_class:
                return f"❌ Classe '{class_name}' déjà existante."
            
            # Ajout de la nouvelle classe
            class_id = self.kb.add_class(f"behavior_{class_name.lower().replace(' ', '_')}", 
                                         class_name)
            
            return f"✅ Classe '{class_name}' ajoutée avec succès! ID: {class_id}"
            
        except Exception as e:
            return f"❌ Erreur lors de l'ajout de la classe: {e}"
    
    def _handle_add_state_machine(self, params: Dict) -> str:
        """
        Gère l'ajout d'une machine à états
        """
        try:
            machine_name = params.get('machine_name')
            if not machine_name:
                return "❌ Nom de la machine manquant dans la requête."
            
            # Vérification de l'existence de la machine
            existing_machine = self.kb.find_machine_by_name(machine_name)
            if existing_machine:
                return f"❌ Machine '{machine_name}' déjà existante."
            
            # Ajout de la nouvelle machine
            machine_id = self.kb.add_machine(f"state_machine_{machine_name.lower().replace(' ', '_')}", 
                                         machine_name)
            
            return f"✅ Machine '{machine_name}' ajoutée avec succès! ID: {machine_id}"
            
        except Exception as e:
            return f"❌ Erreur lors de l'ajout de la machine: {e}"
    
    def _handle_execute_behavior(self, params: Dict) -> str:
        """
        Gère l'exécution d'un comportement
        """
        try:
            behavior_name = params.get('behavior_name')
            if not behavior_name:
                return "❌ Nom du comportement manquant dans la requête."
            
            # Exécution du comportement
            success, message = tools.execute_behavior_tool(behavior_name, self.kb)
            
            if success:
                return f"✅ Comportement '{behavior_name}' exécuté avec succès!\n{message}"
            else:
                return f"❌ Erreur lors de l'exécution du comportement: {message}"
            
        except Exception as e:
            return f"❌ Erreur lors de l'exécution du comportement: {e}"
    
    def _handle_create_semantic_proxy(self, params: Dict) -> str:
        """
        Gère la création d'un proxy sémantique
        """
        try:
            # Implémentation de la création d'un proxy sémantique
            return "🔗 Fonctionnalité de création de proxy sémantique en cours de développement."
            
        except Exception as e:
            return f"❌ Erreur lors de la création du proxy sémantique: {e}"
    
    def _handle_execute_reflection(self, params: Dict) -> str:
        """
        Gère l'exécution d'une réflexion
        """
        try:
            # Implémentation de l'exécution d'une réflexion
            return "🤔 Fonctionnalité d'exécution de réflexion en cours de développement."
            
        except Exception as e:
            return f"❌ Erreur lors de l'exécution de la réflexion: {e}"
    
    def _handle_reflect_class(self, params: Dict) -> str:
        """
        Gère la réflexion sur une classe
        """
        try:
            # Implémentation de la réflexion sur une classe
            return "🔍 Fonctionnalité de réflexion sur une classe en cours de développement."
            
        except Exception as e:
            return f"❌ Erreur lors de la réflexion sur la classe: {e}"
    
    def _handle_instantiate_reflection(self, params: Dict) -> str:
        """
        Gère l'instanciation d'une réflexion
        """
        try:
            # Implémentation de l'instanciation d'une réflexion
            return "🌟 Fonctionnalité d'instanciation de réflexion en cours de développement."
            
        except Exception as e:
            return f"❌ Erreur lors de l'instanciation de la réflexion: {e}"
    
    def _handle_query_ontology(self, params: Dict) -> str:
        """
        Gère les requêtes introspectives sur l'ontologie
        """
        try:
            query_type = params.get('query_type', 'structure')
            class_name = params.get('class_name')
            
            results = tools.query_ontology_tool(query_type, self.kb, class_name=class_name)
            
            if not results:
                return f"❌ Aucun résultat trouvé pour la requête '{query_type}'."
            
            response = f"🔍 Résultats de la requête '{query_type}':\n\n"
            
            if query_type == 'classes':
                for class_info in results:
                    response += f"📋 **{class_info['name']}**\n"
                    response += f"   - URI: {class_info['uri']}\n"
                    response += f"   - Label: {class_info['label']}\n"
                    response += f"   - Instances: {class_info['instances_count']}\n\n"
            
            elif query_type == 'properties':
                for prop_info in results:
                    response += f"🔗 **{prop_info['name']}**\n"
                    response += f"   - Type: {prop_info['type']}\n"
                    response += f"   - Range: {prop_info['range']}\n\n"
            
            elif query_type == 'instances':
                for instance_info in results:
                    response += f"📦 **{instance_info['id']}** ({instance_info['class']})\n"
                    for prop_name, prop_value in instance_info['properties'].items():
                        response += f"   - {prop_name}: {prop_value}\n"
                    response += "\n"
            
            return response
            
        except Exception as e:
            return f"❌ Erreur lors de la requête: {e}"
    
    def _handle_list_orders(self, params: Dict) -> str:
        """
        Gère la liste des commandes
        """
        try:
            orders = tools.get_all_orders_tool(self.kb)
            if not orders:
                return "📋 Aucune commande trouvée."
            
            response = "📋 Liste des commandes:\n\n"
            for order in orders:
                response += f"   ID: {order['order_id']}, Montant: {order['amount']}€, Statut: {order['status']}\n"
            
            return response
            
        except Exception as e:
            return f"❌ Erreur lors de la récupération de la liste des commandes: {e}"
    
    def call_tool_via_mcp(self, tool_name: str, arguments: Dict) -> str:
        """
        Appelle un outil via le serveur MCP
        
        Args:
            tool_name: Nom de l'outil à appeler
            arguments: Arguments de l'outil
        
        Returns:
            str: Résultat de l'appel de l'outil
        """
        if not self.use_mcp or not self.mcp_interface:
            return "❌ Serveur MCP non disponible"
        
        try:
            result = self.mcp_interface.call_tool(tool_name, arguments)
            return f"✅ Résultat de l'outil {tool_name}: {result}"
        except Exception as e:
            return f"❌ Erreur lors de l'appel de l'outil {tool_name} via MCP: {e}"
    
    def list_available_tools_via_mcp(self) -> str:
        """
        Liste les outils disponibles via le serveur MCP
        
        Returns:
            str: Liste des outils disponibles
        """
        if not self.use_mcp or not self.mcp_interface:
            return "❌ Serveur MCP non disponible"
        
        try:
            tools = self.mcp_interface.list_tools()
            if not tools:
                return "📋 Aucun outil disponible via MCP"
            
            response = "🔧 Outils disponibles via MCP:\n\n"
            for tool in tools:
                response += f"   - {tool['name']}: {tool['description']}\n"
            
            return response
        except Exception as e:
            return f"❌ Erreur lors de la récupération des outils MCP: {e}"
    
    def _execute_intent_via_mcp(self, intent: str, params: Dict) -> str:
        """
        Exécute une intention via le serveur MCP
        
        Args:
            intent: Intention à exécuter
            params: Paramètres de l'intention
        
        Returns:
            str: Résultat de l'exécution
        """
        if not self.use_mcp or not self.mcp_interface:
            return "❌ Serveur MCP non disponible"
        
        # Mapping des intentions vers les outils MCP
        intent_to_tool = {
            'create_order': 'create_order',
            'validate_order': 'validate_order',
            'recommend_products': 'recommend_products',
            'check_status': 'get_order_history',
            'process_payment': 'process_payment',
            'add_client': 'add_client',
            'list_clients': 'list_clients',
            'list_orders': 'get_all_orders',
            'introspect_ontology': 'introspect_ontology',
            'extend_ontology': 'extend_ontology',
            'create_instance': 'create_instance',
            'query_ontology': 'query_ontology',
            'add_behavior_class': 'add_behavior_class',
            'add_state_machine': 'add_state_machine',
            'execute_behavior': 'execute_behavior',
            'create_semantic_proxy': 'create_semantic_proxy',
            'execute_reflection': 'execute_method_reflection',
            'reflect_class': 'reflect_class',
            'instantiate_reflection': 'instantiate_by_reflection'
        }
        
        tool_name = intent_to_tool.get(intent)
        if not tool_name:
            return f"❌ Intention '{intent}' non supportée via MCP"
        
        try:
            result = self.mcp_interface.call_tool(tool_name, params)
            return f"✅ Résultat de {intent}: {result}"
        except Exception as e:
            return f"❌ Erreur lors de l'exécution de {intent} via MCP: {e}" 