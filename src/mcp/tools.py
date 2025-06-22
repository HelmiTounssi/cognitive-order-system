"""
Module d'outils (tools) - Fonctions mock simulant des APIs externes
Ces fonctions interagissent avec la base de connaissances et la base vectorielle
"""

import random
import uuid
from typing import Dict, List, Tuple, Optional
from datetime import datetime


def create_order_tool(client_id: str, items_list: List[Dict], 
                     knowledge_base) -> str:
    """
    Crée une nouvelle commande dans le graphe RDF
    
    Args:
        client_id: Identifiant du client
        items_list: Liste des articles avec product_id et quantity
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        str: ID de la commande créée
    """
    try:
        # Génère un ID unique pour la commande
        order_id = f"order_{uuid.uuid4().hex[:8]}"
        
        # Calcule le montant total
        total_amount = 0.0
        for item in items_list:
            product_id = item['product_id']
            quantity = item['quantity']
            
            # Récupère les détails du produit depuis la base de connaissances
            product_details = knowledge_base.get_product_details(product_id)
            if product_details:
                price = float(product_details.get('hasPrice', 0))
                total_amount += price * quantity
        
        # Crée la commande dans le graphe RDF
        knowledge_base.add_order(order_id, client_id, total_amount, "en_attente")
        
        print(f"✅ Commande {order_id} créée pour le client {client_id}")
        print(f"   Montant total: {total_amount:.2f}€")
        print(f"   Articles: {len(items_list)}")
        
        return order_id
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la commande: {e}")
        return None


def check_stock_tool(product_id: str, quantity: int, 
                    knowledge_base) -> Tuple[bool, str]:
    """
    Vérifie la disponibilité en stock d'un produit
    
    Args:
        product_id: Identifiant du produit
        quantity: Quantité demandée
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    try:
        # Récupère les détails du produit
        product_details = knowledge_base.get_product_details(product_id)
        
        if not product_details:
            return False, f"Produit {product_id} non trouvé"
        
        current_stock = int(product_details.get('hasStock', 0))
        product_name = product_details.get('hasName', 'Produit inconnu')
        
        # Simule parfois un échec aléatoire (10% de chance)
        if random.random() < 0.1:
            return False, f"Erreur temporaire lors de la vérification du stock pour {product_name}"
        
        if current_stock >= quantity:
            # Met à jour le stock
            new_stock = current_stock - quantity
            knowledge_base.update_product_stock(product_id, new_stock)
            
            print(f"✅ Stock vérifié pour {product_name}")
            print(f"   Stock disponible: {current_stock} → {new_stock}")
            print(f"   Quantité demandée: {quantity}")
            
            return True, f"Stock suffisant pour {product_name}"
        else:
            print(f"❌ Stock insuffisant pour {product_name}")
            print(f"   Stock disponible: {current_stock}")
            print(f"   Quantité demandée: {quantity}")
            
            return False, f"Stock insuffisant pour {product_name} (disponible: {current_stock}, demandé: {quantity})"
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du stock: {e}")
        return False, f"Erreur lors de la vérification du stock: {e}"


def process_payment_tool(order_id: str, amount: float, 
                        knowledge_base) -> Tuple[bool, str]:
    """
    Traite le paiement d'une commande
    
    Args:
        order_id: Identifiant de la commande
        amount: Montant à payer
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    try:
        # Récupère les détails de la commande
        order_details = knowledge_base.get_order_details(order_id)
        
        if not order_details:
            return False, f"Commande {order_id} non trouvée"
        
        # Simule parfois un échec de paiement (5% de chance)
        if random.random() < 0.05:
            knowledge_base.update_order_status(order_id, "annulee_paiement_echec")
            print(f"❌ Échec du paiement pour la commande {order_id}")
            print(f"   Montant: {amount:.2f}€")
            return False, "Échec du paiement - carte refusée"
        
        # Simule le traitement du paiement
        print(f"💳 Traitement du paiement pour la commande {order_id}")
        print(f"   Montant: {amount:.2f}€")
        
        # Met à jour le statut de la commande
        knowledge_base.update_order_status(order_id, "payee")
        
        print(f"✅ Paiement traité avec succès pour la commande {order_id}")
        return True, "Paiement traité avec succès"
        
    except Exception as e:
        print(f"❌ Erreur lors du traitement du paiement: {e}")
        return False, f"Erreur lors du traitement du paiement: {e}"


def update_order_status_tool(order_id: str, new_status: str, 
                           knowledge_base) -> bool:
    """
    Met à jour le statut d'une commande
    
    Args:
        order_id: Identifiant de la commande
        new_status: Nouveau statut
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        bool: True si la mise à jour a réussi
    """
    try:
        # Vérifie que la commande existe
        order_details = knowledge_base.get_order_details(order_id)
        
        if not order_details:
            print(f"❌ Commande {order_id} non trouvée")
            return False
        
        # Met à jour le statut
        knowledge_base.update_order_status(order_id, new_status)
        
        print(f"✅ Statut de la commande {order_id} mis à jour: {new_status}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du statut: {e}")
        return False


def get_product_details_tool(product_id: str, 
                           knowledge_base) -> Optional[Dict]:
    """
    Récupère les détails d'un produit
    
    Args:
        product_id: Identifiant du produit
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Optional[Dict]: Détails du produit ou None si non trouvé
    """
    try:
        product_details = knowledge_base.get_product_details(product_id)
        
        if product_details:
            print(f"📦 Détails du produit {product_id}:")
            for key, value in product_details.items():
                print(f"   {key}: {value}")
        
        return product_details
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des détails: {e}")
        return None


def get_client_details_tool(client_id: str, knowledge_base, **kwargs) -> Optional[Dict]:
    """
    Récupère les détails d'un client
    
    Args:
        client_id: Identifiant du client
        knowledge_base: Instance de KnowledgeBase
        **kwargs: Paramètres optionnels (ignorés pour cette fonction)
    
    Returns:
        Optional[Dict]: Détails du client ou None si non trouvé
    """
    try:
        client_details = knowledge_base.get_client_details(client_id)
        
        if client_details:
            print(f"👤 Détails du client {client_id}:")
            for key, value in client_details.items():
                print(f"   {key}: {value}")
        
        return client_details
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des détails client: {e}")
        return None


def validate_order_tool(order_id: str, knowledge_base, **kwargs) -> Tuple[bool, str]:
    """
    Valide une commande selon les règles métier
    
    Args:
        order_id: Identifiant de la commande
        knowledge_base: Instance de KnowledgeBase
        **kwargs: Paramètres optionnels (ignorés pour cette fonction)
    
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    try:
        # Récupère les détails de la commande
        order_details = knowledge_base.get_order_details(order_id)
        
        if not order_details:
            return False, f"Commande {order_id} non trouvée"
        
        # Récupère les détails du client
        client_id = order_details.get('hasClient', '')
        client_details = knowledge_base.get_client_details(client_id)
        
        # Récupère le montant
        amount = float(order_details.get('hasAmount', 0))
        
        # Règles de validation simples
        validation_rules = []
        
        # Règle 1: Montant minimum
        if amount < 10:
            validation_rules.append("Montant minimum non atteint (10€)")
        
        # Règle 2: Client valide
        if not client_details:
            validation_rules.append("Client non trouvé")
        
        # Règle 3: Statut initial
        current_status = order_details.get('hasStatus', '')
        if current_status not in ['en_attente', 'nouvelle']:
            validation_rules.append(f"Statut invalide: {current_status}")
        
        # Si toutes les règles sont respectées
        if not validation_rules:
            # Met à jour le statut
            knowledge_base.update_order_status(order_id, "validee")
            
            print(f"✅ Commande {order_id} validée avec succès")
            print(f"   Montant: {amount:.2f}€")
            print(f"   Client: {client_id}")
            
            return True, "Commande validée avec succès"
        else:
            print(f"❌ Commande {order_id} rejetée:")
            for rule in validation_rules:
                print(f"   - {rule}")
            
            return False, f"Commande rejetée: {'; '.join(validation_rules)}"
            
    except Exception as e:
        print(f"❌ Erreur lors de la validation: {e}")
        return False, f"Erreur lors de la validation: {e}"


def recommend_products_tool(query_text: str, vector_store, 
                          knowledge_base, top_k: int = 3) -> List[Dict]:
    """
    Recommande des produits basés sur une requête textuelle
    
    Args:
        query_text: Texte de la requête
        vector_store: Instance de VectorStore
        knowledge_base: Instance de KnowledgeBase
        top_k: Nombre de recommandations
    
    Returns:
        List[Dict]: Liste des produits recommandés
    """
    try:
        # Recherche des produits similaires
        similar_products = vector_store.search_similar_products(query_text, top_k)
        
        recommendations = []
        for product in similar_products:
            product_id = product['product_id']
            
            # Récupère les détails complets du produit
            product_details = knowledge_base.get_product_details(product_id)
            
            if product_details:
                recommendation = {
                    'product_id': product_id,
                    'name': product_details.get('hasName', 'Produit inconnu'),
                    'price': product_details.get('hasPrice', 0),
                    'description': product_details.get('hasDescription', ''),
                    'stock': product_details.get('hasStock', 0),
                    'similarity_score': product['similarity_score']
                }
                recommendations.append(recommendation)
        
        if recommendations:
            print(f"🎯 Recommandations pour '{query_text}':")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec['name']} - {rec['price']}€ (score: {rec['similarity_score']:.2f})")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des recommandations: {e}")
        return []


def get_order_history_tool(client_id: str, knowledge_base, **kwargs) -> List[Dict]:
    """
    Récupère l'historique des commandes d'un client
    
    Args:
        client_id: Identifiant du client
        knowledge_base: Instance de KnowledgeBase
        **kwargs: Paramètres optionnels (ignorés pour cette fonction)
    
    Returns:
        List[Dict]: Historique des commandes
    """
    try:
        # Récupère toutes les commandes
        all_orders = []
        order_uris = knowledge_base.get_instances_of_class(
            "http://example.org/ontology/Order"
        )
        
        for order_uri in order_uris:
            order_id = str(order_uri).split('/')[-1]
            order_details = knowledge_base.get_order_details(order_id)
            
            if order_details and order_details.get('hasClient') == client_id:
                all_orders.append({
                    'order_id': order_id,
                    'amount': order_details.get('hasAmount', 0),
                    'status': order_details.get('hasStatus', 'inconnu'),
                    'date': order_details.get('hasDate', 'N/A')
                })
        
        # Trie par date (plus récent en premier)
        all_orders.sort(key=lambda x: x['date'], reverse=True)
        
        print(f"📋 Historique des commandes pour le client {client_id}:")
        print(f"   Nombre de commandes: {len(all_orders)}")
        
        total_amount = sum(order['amount'] for order in all_orders)
        print(f"   Montant total: {total_amount:.2f}€")
        
        for order in all_orders[:5]:  # Affiche les 5 dernières
            print(f"   - {order['order_id']}: {order['amount']}€ ({order['status']})")
        
        if len(all_orders) > 5:
            print(f"   ... et {len(all_orders) - 5} autres commandes")
        
        return all_orders
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'historique: {e}")
        return []


def add_client_tool(name: str, email: str, knowledge_base) -> Tuple[bool, str]:
    """
    Ajoute un nouveau client dans la base de connaissances
    
    Args:
        name: Nom du client
        email: Email du client
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, message avec client_id si succès)
    """
    try:
        # Vérifie que l'email n'est pas déjà utilisé
        existing_clients = knowledge_base.get_instances_of_class(
            "http://example.org/ontology/Client"
        )
        
        for client_uri in existing_clients:
            client_details = knowledge_base.get_client_details(client_uri)
            if client_details and client_details.get('hasEmail') == email:
                return False, f"Un client avec l'email {email} existe déjà"
        
        # Génère un ID unique pour le client
        client_id = f"client_{uuid.uuid4().hex[:8]}"
        
        # Ajoute le client dans la base de connaissances
        knowledge_base.add_client(client_id, name, email)
        
        print(f"✅ Nouveau client ajouté:")
        print(f"   ID: {client_id}")
        print(f"   Nom: {name}")
        print(f"   Email: {email}")
        
        return True, f"Client {name} ajouté avec succès (ID: {client_id})"
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout du client: {e}")
        return False, f"Erreur lors de l'ajout du client: {e}"


def list_clients_tool(knowledge_base, **kwargs) -> List[Dict]:
    """
    Liste tous les clients dans la base de connaissances
    
    Args:
        knowledge_base: Instance de KnowledgeBase
        **kwargs: Paramètres optionnels (ignorés pour cette fonction)
    
    Returns:
        List[Dict]: Liste des clients avec leurs détails
    """
    try:
        # Utilise la méthode get_clients de la base de connaissances
        clients = knowledge_base.get_clients()
        
        print(f"📋 Liste des clients ({len(clients)} clients):")
        for client in clients:
            print(f"   - {client.get('name', 'N/A')} ({client.get('email', 'N/A')}) - ID: {client.get('id', 'N/A')}")
        
        return clients
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des clients: {e}")
        return []


# ===== OUTILS D'INTROSPECTION ET RÉFLEXIVITÉ =====

def introspect_ontology_tool(knowledge_base, **kwargs) -> Dict:
    """
    Introspection complète de l'ontologie
    
    Args:
        knowledge_base: Instance de KnowledgeBase
        **kwargs: Paramètres optionnels (ignorés pour cette fonction)
    
    Returns:
        Dict: Structure complète de l'ontologie
    """
    try:
        ontology_info = knowledge_base.introspect_ontology()
        
        print("🔍 Introspection de l'ontologie:")
        print(f"   Classes: {len(ontology_info.get('classes', []))}")
        print(f"   Propriétés: {len(ontology_info.get('properties', []))}")
        print(f"   Namespaces: {len(ontology_info.get('namespaces', {}))}")
        
        for class_info in ontology_info.get('classes', []):
            print(f"   - {class_info['name']}: {class_info['instances_count']} instances")
        
        return ontology_info
        
    except Exception as e:
        print(f"❌ Erreur lors de l'introspection: {e}")
        return {}


def extend_ontology_tool(class_name: str, properties: List[Dict], 
                        knowledge_base, namespace: str = None) -> Tuple[bool, str]:
    """
    Étend dynamiquement l'ontologie avec une nouvelle classe
    
    Args:
        class_name: Nom de la nouvelle classe
        properties: Liste des propriétés avec leurs types
        knowledge_base: Instance de KnowledgeBase
        namespace: Namespace personnalisé (optionnel)
    
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    try:
        success = knowledge_base.extend_ontology_dynamically(class_name, properties, namespace)
        
        if success:
            return True, f"Classe '{class_name}' ajoutée avec succès à l'ontologie"
        else:
            return False, f"Échec de l'ajout de la classe '{class_name}'"
        
    except Exception as e:
        print(f"❌ Erreur lors de l'extension de l'ontologie: {e}")
        return False, f"Erreur lors de l'extension: {e}"


def create_instance_tool(class_name: str, properties: Dict, 
                        knowledge_base, instance_id: str = None) -> Tuple[bool, str]:
    """
    Crée dynamiquement une instance d'une classe
    
    Args:
        class_name: Nom de la classe
        properties: Dictionnaire des propriétés et valeurs
        knowledge_base: Instance de KnowledgeBase
        instance_id: ID personnalisé (optionnel)
    
    Returns:
        Tuple[bool, str]: (succès, message avec ID si succès)
    """
    try:
        instance_id = knowledge_base.create_instance_dynamically(class_name, properties, instance_id)
        
        if instance_id:
            return True, f"Instance '{instance_id}' de type '{class_name}' créée avec succès"
        else:
            return False, f"Échec de la création de l'instance de type '{class_name}'"
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'instance: {e}")
        return False, f"Erreur lors de la création: {e}"


def query_ontology_tool(query_type: str, knowledge_base, **kwargs) -> List[Dict]:
    """
    Requête introspective de l'ontologie
    
    Args:
        query_type: Type de requête ('classes', 'properties', 'instances', 'structure')
        knowledge_base: Instance de KnowledgeBase
        **kwargs: Paramètres spécifiques à la requête
    
    Returns:
        List[Dict]: Résultats de la requête
    """
    try:
        results = knowledge_base.query_ontology_introspectively(query_type, **kwargs)
        
        print(f"🔍 Requête '{query_type}' - {len(results)} résultats")
        
        if query_type == 'classes':
            for class_info in results:
                print(f"   - {class_info['name']}: {class_info['instances_count']} instances")
        elif query_type == 'properties':
            for prop_info in results:
                print(f"   - {prop_info['name']} ({prop_info['type']}): {prop_info['range']}")
        elif query_type == 'instances':
            for instance_info in results:
                print(f"   - {instance_info['id']} ({instance_info['class']})")
        
        return results
        
    except Exception as e:
        print(f"❌ Erreur lors de la requête: {e}")
        return []


def get_all_orders_tool(knowledge_base, **kwargs) -> List[Dict]:
    """
    Récupère toutes les commandes dans la base de connaissances
    
    Args:
        knowledge_base: Instance de KnowledgeBase
        **kwargs: Paramètres optionnels (ignorés pour cette fonction)
    
    Returns:
        List[Dict]: Liste des commandes avec leurs détails
    """
    try:
        orders = []
        order_uris = knowledge_base.get_instances_of_class(
            "http://example.org/ontology/Order"
        )
        
        for order_uri in order_uris:
            order_id = str(order_uri).split('/')[-1]
            order_details = knowledge_base.get_order_details(order_id)
            if order_details:
                orders.append({
                    'order_id': order_id,
                    'client_id': order_details.get('hasClient', 'N/A'),
                    'amount': order_details.get('hasAmount', 'N/A'),
                    'status': order_details.get('hasStatus', 'N/A'),
                    'date': order_details.get('hasDate', 'N/A')
                })
        
        print(f"📋 Liste des commandes ({len(orders)} commandes):")
        for order in orders:
            print(f"   - {order['order_id']}: {order['amount']}€ ({order['status']})")
        
        return orders
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des commandes: {e}")
        return []


def add_behavior_class_tool(class_name: str, methods: List[Dict], 
                           knowledge_base) -> Tuple[bool, str]:
    """
    Ajoute une classe avec des comportements (méthodes)
    
    Args:
        class_name: Nom de la classe
        methods: Liste des méthodes avec leurs paramètres et types de retour
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    try:
        success = knowledge_base.add_behavior_class(class_name, methods)
        
        if success:
            print(f"✅ Classe comportementale '{class_name}' créée avec succès")
            print(f"   Méthodes ajoutées: {len(methods)}")
            for method in methods:
                print(f"     - {method['name']}")
                if 'parameters' in method:
                    params = [p['name'] for p in method['parameters']]
                    print(f"       Paramètres: {', '.join(params)}")
                if 'return_type' in method:
                    print(f"       Retour: {method['return_type']}")
            
            return True, f"Classe comportementale '{class_name}' ajoutée avec succès"
        else:
            return False, f"Erreur lors de la création de la classe comportementale '{class_name}'"
            
    except Exception as e:
        return False, f"Erreur: {e}"


def add_state_machine_tool(class_name: str, states: List[str], 
                          transitions: List[Dict], 
                          knowledge_base) -> Tuple[bool, str]:
    """
    Ajoute une machine à états pour une classe
    
    Args:
        class_name: Nom de la classe
        states: Liste des états possibles
        transitions: Liste des transitions
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    try:
        success = knowledge_base.add_state_machine(class_name, states, transitions)
        
        if success:
            print(f"✅ Machine à états pour '{class_name}' créée avec succès")
            print(f"   États: {', '.join(states)}")
            print(f"   Transitions: {len(transitions)}")
            for trans in transitions:
                trigger = trans.get('trigger', 'automatique')
                print(f"     - {trans['from']} -> {trans['to']} (trigger: {trigger})")
            
            return True, f"Machine à états pour '{class_name}' ajoutée avec succès"
        else:
            return False, f"Erreur lors de la création de la machine à états pour '{class_name}'"
            
    except Exception as e:
        return False, f"Erreur: {e}"


def execute_behavior_tool(instance_id: str, method_name: str, 
                         parameters: Dict, knowledge_base) -> Tuple[bool, str]:
    """
    Exécute un comportement (méthode) sur une instance
    
    Args:
        instance_id: ID de l'instance
        method_name: Nom de la méthode à exécuter
        parameters: Paramètres de la méthode
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, résultat)
    """
    try:
        # Récupère les détails de l'instance
        instance_details = knowledge_base.get_instance_details(instance_id)
        if not instance_details:
            return False, f"Instance '{instance_id}' non trouvée"
        
        # Simule l'exécution du comportement
        print(f"🔄 Exécution de '{method_name}' sur l'instance '{instance_id}'")
        print(f"   Paramètres: {parameters}")
        
        # Logique d'exécution selon la méthode
        if method_name == "passer_commande":
            # Simulation de création de commande
            order_id = f"order_{uuid.uuid4().hex[:8]}"
            result = f"Commande créée: {order_id}"
            
        elif method_name == "payer":
            # Simulation de paiement
            amount = parameters.get('montant', 0)
            result = f"Paiement de {amount}€ traité"
            
        elif method_name == "changer_etat":
            # Simulation de changement d'état
            new_state = parameters.get('nouvel_etat', 'inconnu')
            result = f"État changé vers: {new_state}"
            
        else:
            result = f"Méthode '{method_name}' exécutée avec succès"
        
        print(f"   Résultat: {result}")
        return True, result
        
    except Exception as e:
        return False, f"Erreur lors de l'exécution: {e}"


def create_semantic_proxy_tool(knowledge_base, class_name: str, instance_id: str = None) -> Tuple[bool, str]:
    """
    Crée un proxy sémantique pour une classe ou une instance
    
    Args:
        knowledge_base: Instance de KnowledgeBase
        class_name: Nom de la classe
        instance_id: ID de l'instance (optionnel)
    
    Returns:
        Tuple[bool, str]: (succès, message avec proxy_id)
    """
    try:
        from knowledge_base import SemanticProxy
        
        proxy_manager = SemanticProxy(knowledge_base)
        proxy = proxy_manager.create_proxy(class_name, instance_id)
        
        if proxy:
            proxy_id = f"proxy_{class_name}_{instance_id or 'class'}"
            return True, f"Proxy sémantique créé: {proxy_id}"
        else:
            return False, "Erreur lors de la création du proxy"
            
    except Exception as e:
        return False, f"Erreur: {e}"


def execute_method_reflection_tool(proxy_id: str, method_name: str, 
                                  parameters: Dict, knowledge_base) -> Tuple[bool, str]:
    """
    Exécute une méthode par réflexion via un proxy sémantique
    
    Args:
        proxy_id: ID du proxy
        method_name: Nom de la méthode
        parameters: Paramètres de la méthode
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, résultat)
    """
    try:
        from knowledge_base import SemanticProxy
        
        # Parse le proxy_id pour extraire class_name et instance_id
        parts = proxy_id.replace('proxy_', '').split('_')
        if len(parts) >= 2:
            class_name = parts[0]
            instance_id = '_'.join(parts[1:]) if len(parts) > 1 else None
        else:
            return False, "Format de proxy_id invalide"
        
        proxy_manager = SemanticProxy(knowledge_base)
        proxy = proxy_manager.get_proxy(class_name, instance_id)
        
        if not proxy:
            proxy = proxy_manager.create_proxy(class_name, instance_id)
        
        if proxy:
            # Exécute la méthode par réflexion
            result = proxy._execute_method(method_name, **parameters)
            return True, f"Résultat: {result}"
        else:
            return False, "Proxy non trouvé"
            
    except Exception as e:
        return False, f"Erreur lors de l'exécution: {e}"


def reflect_class_tool(class_name: str, knowledge_base) -> Tuple[bool, str]:
    """
    Effectue une réflexion complète sur une classe
    
    Args:
        class_name: Nom de la classe
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, structure de la classe)
    """
    try:
        from knowledge_base import SemanticProxy
        
        proxy_manager = SemanticProxy(knowledge_base)
        structure = proxy_manager.reflect_class_structure(class_name)
        
        if structure:
            # Formatage de la sortie
            output = f"🔍 Réflexion sur la classe '{class_name}':\n"
            output += f"   URI: {structure.get('class_uri', 'N/A')}\n"
            output += f"   Propriétés: {', '.join(structure.get('properties', []))}\n"
            output += f"   Méthodes: {len(structure.get('methods', []))}\n"
            output += f"   Instances: {structure.get('instances_count', 0)}\n"
            
            # Détail des méthodes
            for method in structure.get('methods', []):
                output += f"     - {method['name']}"
                if method.get('parameters'):
                    params = [p['name'] for p in method['parameters']]
                    output += f"({', '.join(params)})"
                if method.get('return_type'):
                    output += f" -> {method['return_type']}"
                output += "\n"
            
            return True, output
        else:
            return False, f"Classe '{class_name}' non trouvée"
            
    except Exception as e:
        return False, f"Erreur lors de la réflexion: {e}"


def instantiate_by_reflection_tool(class_name: str, properties: Dict, 
                                  knowledge_base) -> Tuple[bool, str]:
    """
    Instancie un objet par réflexion
    
    Args:
        class_name: Nom de la classe
        properties: Propriétés de l'instance
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, instance_id)
    """
    try:
        # Vérifie que la classe existe
        class_uri = f"{knowledge_base.ns['ex']}{class_name}"
        if not knowledge_base.class_exists(class_uri):
            return False, f"Classe '{class_name}' non trouvée"
        
        # Crée l'instance par réflexion
        instance_id = knowledge_base.create_instance_dynamically(class_name, properties)
        
        if instance_id:
            # Crée automatiquement un proxy pour cette instance
            from knowledge_base import SemanticProxy
            proxy_manager = SemanticProxy(knowledge_base)
            proxy = proxy_manager.create_proxy(class_name, instance_id)
            
            return True, f"Instance créée par réflexion: {instance_id}"
        else:
            return False, "Erreur lors de la création de l'instance"
            
    except Exception as e:
        return False, f"Erreur: {e}"


def list_proxy_methods_tool(class_name: str, knowledge_base) -> Tuple[bool, str]:
    """
    Liste toutes les méthodes disponibles pour un proxy
    
    Args:
        class_name: Nom de la classe
        knowledge_base: Instance de KnowledgeBase
    
    Returns:
        Tuple[bool, str]: (succès, liste des méthodes)
    """
    try:
        from knowledge_base import SemanticProxy
        
        proxy_manager = SemanticProxy(knowledge_base)
        methods = proxy_manager.list_available_methods(class_name)
        
        if methods:
            output = f"📋 Méthodes disponibles pour '{class_name}':\n"
            for method in methods:
                output += f"   - {method['name']}"
                if method.get('parameters'):
                    params = [p['name'] for p in method['parameters']]
                    output += f"({', '.join(params)})"
                if method.get('return_type'):
                    output += f" -> {method['return_type']}"
                output += "\n"
            
            return True, output
        else:
            return False, f"Aucune méthode trouvée pour '{class_name}'"
            
    except Exception as e:
        return False, f"Erreur: {e}" 