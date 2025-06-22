"""
Module Base de Connaissances - Gestion de l'ontologie et des entités
Implémente une base de connaissances sémantique avec support RDF et réflexion
"""

import json
import re
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
import uuid


class KnowledgeBase:
    def __init__(self, vector_store=None):
        """Initialise la base de connaissances avec un graphe RDF"""
        self.graph = Graph()
        
        # Initialise le vector store si non fourni
        self.vector_store = vector_store
        
        # Définition des namespaces
        self.ns = {
            'rdf': RDF,
            'rdfs': RDFS,
            'owl': OWL,
            'xsd': XSD,
            'ex': Namespace('http://example.org/ontology/'),
            'client': Namespace('http://example.org/client/'),
            'product': Namespace('http://example.org/product/'),
            'order': Namespace('http://example.org/order/'),
            'action': Namespace('http://example.org/action/'),
            'tool': Namespace('http://example.org/tool/'),
            'instance': Namespace('http://example.org/instance/')
        }
        
        # Bind des namespaces au graphe
        for prefix, namespace in self.ns.items():
            self.graph.bind(prefix, namespace)
        
        # Initialisation minimale de l'ontologie (aucune classe métier ni instance)
        # Laisse la structure vide pour extension dynamique
        # self._initialize_ontology()  # SUPPRIMÉ
        # self._load_initial_data()    # SUPPRIMÉ
    
    def _initialize_ontology(self):
        """Définit les classes et propriétés de l'ontologie"""
        ex = self.ns['ex']
        
        # Classes principales
        classes = [
            (ex.Client, "Client"),
            (ex.Product, "Product"),
            (ex.Order, "Order"),
            (ex.OrderStatus, "OrderStatus"),
            (ex.Action, "Action"),
            (ex.ServiceTool, "ServiceTool")
        ]
        
        for class_uri, label in classes:
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(label)))
        
        # Propriétés des objets
        properties = [
            (ex.hasName, "hasName", XSD.string),
            (ex.hasEmail, "hasEmail", XSD.string),
            (ex.hasPrice, "hasPrice", XSD.decimal),
            (ex.hasStock, "hasStock", XSD.integer),
            (ex.hasDescription, "hasDescription", XSD.string),
            (ex.hasQuantity, "hasQuantity", XSD.integer),
            (ex.hasStatus, "hasStatus", XSD.string),
            (ex.hasAmount, "hasAmount", XSD.decimal),
            (ex.hasDate, "hasDate", XSD.dateTime),
            (ex.hasClient, "hasClient", ex.Client),
            (ex.hasProduct, "hasProduct", ex.Product),
            (ex.hasOrder, "hasOrder", ex.Order)
        ]
        
        for prop_uri, label, range_type in properties:
            is_datatype = range_type in [XSD.string, XSD.decimal,
                                        XSD.integer, XSD.dateTime]
            prop_type = (OWL.DatatypeProperty if is_datatype
                        else OWL.ObjectProperty)
            self.graph.add((prop_uri, RDF.type, prop_type))
            self.graph.add((prop_uri, RDFS.label, Literal(label)))
            self.graph.add((prop_uri, RDFS.range, range_type))
        
        # Statuts de commande
        statuses = ["en_attente", "validee", "payee", "livree",
                   "annulee_stock_insuffisant",
                   "annulee_paiement_echec"]
        for status in statuses:
            status_uri = URIRef(f"{ex}OrderStatus_{status}")
            self.graph.add((status_uri, RDF.type, ex.OrderStatus))
            self.graph.add((status_uri, RDFS.label, Literal(status)))
    
    def _load_initial_data(self):
        """Charge les données initiales (clients, produits)"""
        # Clients initiaux
        clients_data = [
            ("John Doe", "john.doe@email.com"),
            ("Jane Smith", "jane.smith@email.com"),
            ("Bob Johnson", "bob.johnson@email.com")
        ]
        
        print("📚 Chargement des clients initiaux...")
        for name, email in clients_data:
            client_id = f"client_{uuid.uuid4().hex[:8]}"
            self.add_client(client_id, name, email)
            print(f"   ✅ Client ajouté: {name} ({client_id})")
        
        # Produits initiaux
        products_data = [
            ("Super Laptop", 1200.0, 10,
             "Ordinateur portable haute performance"),
            ("Gaming Mouse", 89.99, 25,
             "Souris gaming avec capteur optique avancé"),
            ("Mechanical Keyboard", 149.99, 15,
             "Clavier mécanique avec switches Cherry MX"),
            ("Gaming Mousepad", 29.99, 50,
             "Tapis de souris XXL RGB"),
            ("Wireless Headset", 199.99, 8,
             "Casque sans fil avec micro intégré"),
            ("Laptop X", 899.99, 5,
             "Ordinateur portable milieu de gamme"),
            ("USB-C Hub", 45.99, 30,
             "Hub USB-C multi-ports"),
            ("External SSD", 129.99, 12,
             "SSD externe 1TB haute vitesse")
        ]
        
        print("📚 Chargement des produits initiaux...")
        for name, price, stock, description in products_data:
            product_id = f"product_{uuid.uuid4().hex[:8]}"
            self.add_product(product_id, name, price, stock, description)
            print(f"   ✅ Produit ajouté: {name} ({product_id})")
        
        print(f"📊 Base de connaissances initialisée avec {len(clients_data)} clients et {len(products_data)} produits")
    
    def add_triple(self, subject: str, predicate: str, object_value: str):
        """Ajoute un triplet au graphe RDF"""
        subject_uri = URIRef(subject)
        predicate_uri = URIRef(predicate)
        
        if object_value.startswith('http'):
            object_uri = URIRef(object_value)
        else:
            object_uri = Literal(object_value)
        
        self.graph.add((subject_uri, predicate_uri, object_uri))
    
    def get_properties(self, subject_uri: str, 
                      predicate_uri: str = None) -> List[Tuple]:
        """Récupère les propriétés d'un sujet"""
        subject = URIRef(subject_uri)
        if predicate_uri:
            predicate = URIRef(predicate_uri)
            results = self.graph.objects(subject, predicate)
        else:
            results = self.graph.predicate_objects(subject)
        
        return list(results)
    
    def get_instances_of_class(self, class_uri: str) -> List[str]:
        """Récupère toutes les instances d'une classe"""
        class_ref = URIRef(class_uri)
        instances = []
        
        for s, p, o in self.graph.triples((None, RDF.type, class_ref)):
            instances.append(str(s))
        
        return instances
    
    def update_triple(self, subject: str, predicate: str, old_object: str,
                     new_object: str):
        """Met à jour un triplet dans le graphe"""
        subject_uri = URIRef(subject)
        predicate_uri = URIRef(predicate)
        
        # Supprime l'ancien triplet
        if old_object.startswith('http'):
            old_obj_uri = URIRef(old_object)
        else:
            old_obj_uri = Literal(old_object)
        
        self.graph.remove((subject_uri, predicate_uri, old_obj_uri))
        
        # Ajoute le nouveau triplet
        if new_object.startswith('http'):
            new_obj_uri = URIRef(new_object)
        else:
            new_obj_uri = Literal(new_object)
        
        self.graph.add((subject_uri, predicate_uri, new_obj_uri))
    
    def add_client(self, client_id: str, name: str, email: str) -> str:
        """Ajoute un nouveau client"""
        # Vérifie si la classe Client existe, sinon la crée
        if not self._class_exists(self.ns['ex'].Client):
            self._create_client_class()
        
        client_uri = URIRef(f"{self.ns['client']}{client_id}")
        
        self.graph.add((client_uri, RDF.type, self.ns['ex'].Client))
        self.graph.add((client_uri, self.ns['ex'].hasName, Literal(name)))
        self.graph.add((client_uri, self.ns['ex'].hasEmail, Literal(email)))
        
        return client_id
    
    def _class_exists(self, class_uri) -> bool:
        """Vérifie si une classe existe dans le graphe"""
        return (class_uri, RDF.type, OWL.Class) in self.graph
    
    def _create_client_class(self):
        """Crée la classe Client et ses propriétés"""
        ex = self.ns['ex']
        
        # Crée la classe Client
        self.graph.add((ex.Client, RDF.type, OWL.Class))
        self.graph.add((ex.Client, RDFS.label, Literal("Client")))
        
        # Crée les propriétés hasName et hasEmail si elles n'existent pas
        if not self._property_exists(ex.hasName):
            self.graph.add((ex.hasName, RDF.type, OWL.DatatypeProperty))
            self.graph.add((ex.hasName, RDFS.label, Literal("hasName")))
            self.graph.add((ex.hasName, RDFS.range, XSD.string))
        
        if not self._property_exists(ex.hasEmail):
            self.graph.add((ex.hasEmail, RDF.type, OWL.DatatypeProperty))
            self.graph.add((ex.hasEmail, RDFS.label, Literal("hasEmail")))
            self.graph.add((ex.hasEmail, RDFS.range, XSD.string))
        
        print("✅ Classe Client créée automatiquement")
    
    def _property_exists(self, property_uri) -> bool:
        """Vérifie si une propriété existe dans le graphe"""
        return ((property_uri, RDF.type, OWL.DatatypeProperty) in self.graph or 
                (property_uri, RDF.type, OWL.ObjectProperty) in self.graph)
    
    def add_product(self, product_id: str, name: str, price: float,
                   stock: int, description: str) -> str:
        """Ajoute un nouveau produit"""
        product_uri = URIRef(f"{self.ns['product']}{product_id}")
        
        self.graph.add((product_uri, RDF.type, self.ns['ex'].Product))
        self.graph.add((product_uri, self.ns['ex'].hasName, Literal(name)))
        self.graph.add((product_uri, self.ns['ex'].hasPrice, Literal(price)))
        self.graph.add((product_uri, self.ns['ex'].hasStock, Literal(stock)))
        self.graph.add((product_uri, self.ns['ex'].hasDescription,
                       Literal(description)))
        
        return product_id
    
    def add_order(self, order_id: str, client_id: str, amount: float,
                 status: str = "en_attente") -> str:
        """Ajoute une nouvelle commande"""
        order_uri = URIRef(f"{self.ns['order']}{order_id}")
        client_uri = URIRef(f"{self.ns['client']}{client_id}")
        
        self.graph.add((order_uri, RDF.type, self.ns['ex'].Order))
        self.graph.add((order_uri, self.ns['ex'].hasClient, client_uri))
        self.graph.add((order_uri, self.ns['ex'].hasAmount, Literal(amount)))
        self.graph.add((order_uri, self.ns['ex'].hasStatus, Literal(status)))
        
        return order_id
    
    def find_client_by_name(self, name: str) -> Optional[str]:
        """Trouve un client par son nom"""
        for s, p, o in self.graph.triples((None, self.ns['ex'].hasName,
                                         Literal(name))):
            if (s, RDF.type, self.ns['ex'].Client) in self.graph:
                return str(s).split('/')[-1]  # Retourne l'ID du client
        return None
    
    def find_product_by_name(self, name: str) -> Optional[str]:
        """Trouve un produit par son nom"""
        for s, p, o in self.graph.triples((None, self.ns['ex'].hasName,
                                         Literal(name))):
            if (s, RDF.type, self.ns['ex'].Product) in self.graph:
                return str(s).split('/')[-1]  # Retourne l'ID du produit
        return None
    
    def get_product_details(self, product_id: str) -> Dict:
        """Récupère les détails d'un produit"""
        product_uri = URIRef(f"{self.ns['product']}{product_id}")
        details = {}
        
        for s, p, o in self.graph.triples((product_uri, None, None)):
            if p == RDF.type:
                continue
            prop_name = str(p).split('/')[-1]
            details[prop_name] = str(o)
        
        return details
    
    def get_client_details(self, client_id: str) -> Dict:
        """Récupère les détails d'un client"""
        client_uri = URIRef(f"{self.ns['client']}{client_id}")
        details = {}
        
        for s, p, o in self.graph.triples((client_uri, None, None)):
            if p == RDF.type:
                continue
            prop_name = str(p).split('/')[-1]
            details[prop_name] = str(o)
        
        return details
    
    def get_order_details(self, order_id: str) -> Dict:
        """Récupère les détails d'une commande"""
        order_uri = URIRef(f"{self.ns['order']}{order_id}")
        details = {}
        
        for s, p, o in self.graph.triples((order_uri, None, None)):
            if p == RDF.type:
                continue
            prop_name = str(p).split('/')[-1]
            details[prop_name] = str(o)
        
        return details
    
    def update_order_status(self, order_id: str, new_status: str):
        """Met à jour le statut d'une commande"""
        order_uri = URIRef(f"{self.ns['order']}{order_id}")
        
        # Supprime l'ancien statut
        for s, p, o in self.graph.triples((order_uri, self.ns['ex'].hasStatus,
                                         None)):
            self.graph.remove((s, p, o))
        
        # Ajoute le nouveau statut
        self.graph.add((order_uri, self.ns['ex'].hasStatus, 
                       Literal(new_status)))
    
    def update_product_stock(self, product_id: str, new_stock: int):
        """Met à jour le stock d'un produit"""
        product_uri = URIRef(f"{self.ns['product']}{product_id}")
        
        # Supprime l'ancien stock
        for s, p, o in self.graph.triples((product_uri, self.ns['ex'].hasStock,
                                         None)):
            self.graph.remove((s, p, o))
        
        # Ajoute le nouveau stock
        self.graph.add((product_uri, self.ns['ex'].hasStock, 
                       Literal(new_stock)))
    
    def save_graph_to_file(self, filename: str):
        """Sauvegarde le graphe dans un fichier Turtle"""
        self.graph.serialize(destination=filename, format='turtle')
    
    def load_graph_from_file(self, filename: str):
        """Charge le graphe depuis un fichier Turtle"""
        self.graph.parse(filename, format='turtle')
    
    def query_graph(self, sparql_query: str) -> List[Dict]:
        """Exécute une requête SPARQL sur le graphe"""
        try:
            results = self.graph.query(sparql_query)
            return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de la requête SPARQL: {e}")
            return []
    
    def get_clients(self) -> List[Dict]:
        """
        Récupère tous les clients avec leurs détails
        
        Returns:
            List[Dict]: Liste des clients avec id, name, email
        """
        try:
            clients = []
            # Utilise le namespace correct au lieu de l'URI hardcodée
            client_uris = self.get_instances_of_class(str(self.ns['ex'].Client))
            
            for client_uri in client_uris:
                # Extrait l'ID du client depuis l'URI
                client_id = str(client_uri).split('/')[-1]
                client_details = self.get_client_details(client_id)
                if client_details:
                    clients.append({
                        'id': client_id,
                        'name': client_details.get('hasName', 'N/A'),
                        'email': client_details.get('hasEmail', 'N/A')
                    })
            
            return clients
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des clients: {e}")
            return []
    
    # ===== MÉTHODES D'INTROSPECTION ET RÉFLEXIVITÉ =====
    
    def introspect_ontology(self) -> Dict:
        """
        Introspection de l'ontologie - analyse la structure actuelle
        
        Returns:
            Dict: Structure complète de l'ontologie
        """
        try:
            ontology_info = {
                'classes': [],
                'properties': [],
                'instances': {},
                'namespaces': {}
            }
            
            # Analyse des namespaces
            for prefix, namespace in self.ns.items():
                ontology_info['namespaces'][prefix] = str(namespace)
            
            # Analyse des classes
            for s, p, o in self.graph.triples((None, RDF.type, OWL.Class)):
                class_info = {
                    'uri': str(s),
                    'name': str(s).split('/')[-1],
                    'label': self._get_label(s),
                    'instances_count': len(list(self.graph.triples((None, RDF.type, s))))
                }
                ontology_info['classes'].append(class_info)
            
            # Analyse des propriétés
            for s, p, o in self.graph.triples((None, RDF.type, OWL.DatatypeProperty)):
                prop_info = {
                    'uri': str(s),
                    'name': str(s).split('/')[-1],
                    'label': self._get_label(s),
                    'type': 'DatatypeProperty',
                    'range': self._get_property_range(s)
                }
                ontology_info['properties'].append(prop_info)
            
            for s, p, o in self.graph.triples((None, RDF.type, OWL.ObjectProperty)):
                prop_info = {
                    'uri': str(s),
                    'name': str(s).split('/')[-1],
                    'label': self._get_label(s),
                    'type': 'ObjectProperty',
                    'range': self._get_property_range(s)
                }
                ontology_info['properties'].append(prop_info)
            
            # Analyse des instances par classe
            for class_info in ontology_info['classes']:
                class_uri = URIRef(class_info['uri'])
                instances = []
                for s, p, o in self.graph.triples((None, RDF.type, class_uri)):
                    instance_info = {
                        'uri': str(s),
                        'id': str(s).split('/')[-1],
                        'properties': self._get_instance_properties(s)
                    }
                    instances.append(instance_info)
                ontology_info['instances'][class_info['name']] = instances
            
            return ontology_info
            
        except Exception as e:
            print(f"❌ Erreur lors de l'introspection: {e}")
            return {}
    
    def _get_label(self, uri) -> str:
        """Récupère le label d'une URI"""
        for s, p, o in self.graph.triples((uri, RDFS.label, None)):
            return str(o)
        return str(uri).split('/')[-1]
    
    def _get_property_range(self, prop_uri) -> str:
        """Récupère le range d'une propriété"""
        for s, p, o in self.graph.triples((prop_uri, RDFS.range, None)):
            return str(o)
        return "unknown"
    
    def _get_instance_properties(self, instance_uri) -> Dict:
        """Récupère toutes les propriétés d'une instance"""
        properties = {}
        for s, p, o in self.graph.triples((instance_uri, None, None)):
            if p != RDF.type:
                prop_name = str(p).split('/')[-1]
                properties[prop_name] = str(o)
        return properties
    
    def extend_ontology_dynamically(self, class_name: str, properties: List[Dict], 
                                   namespace: str = None) -> bool:
        """
        Étend dynamiquement l'ontologie en ajoutant une nouvelle classe
        
        Args:
            class_name: Nom de la nouvelle classe
            properties: Liste des propriétés avec leurs types
            namespace: Namespace personnalisé (optionnel)
        
        Returns:
            bool: True si l'extension a réussi
        """
        try:
            # Utilise le namespace par défaut ou crée un nouveau
            if namespace:
                if namespace not in self.ns:
                    self.ns[namespace] = Namespace(f"http://example.org/{namespace}/")
                    self.graph.bind(namespace, self.ns[namespace])
                ns_uri = self.ns[namespace]
            else:
                ns_uri = self.ns['ex']
            
            # Crée la nouvelle classe
            class_uri = URIRef(f"{ns_uri}{class_name}")
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(class_name)))
            
            print(f"✅ Nouvelle classe créée: {class_name}")
            
            # Crée les propriétés
            for prop_info in properties:
                prop_name = prop_info['name']
                prop_type = prop_info.get('type', 'string')  # string, int, float, uri
                prop_label = prop_info.get('label', prop_name)
                
                prop_uri = URIRef(f"{ns_uri}{prop_name}")
                
                # Détermine le type de propriété
                if prop_type in ['string', 'int', 'float', 'dateTime']:
                    prop_class = OWL.DatatypeProperty
                    range_type = getattr(XSD, prop_type) if hasattr(XSD, prop_type) else XSD.string
                else:
                    prop_class = OWL.ObjectProperty
                    range_type = URIRef(f"{ns_uri}{prop_type}")
                
                self.graph.add((prop_uri, RDF.type, prop_class))
                self.graph.add((prop_uri, RDFS.label, Literal(prop_label)))
                self.graph.add((prop_uri, RDFS.range, range_type))
                
                print(f"   ✅ Propriété ajoutée: {prop_name} ({prop_type})")
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'extension de l'ontologie: {e}")
            return False
    
    def create_instance_dynamically(self, class_name: str, properties: Dict, 
                                   instance_id: str = None) -> str:
        """
        Crée dynamiquement une instance d'une classe
        
        Args:
            class_name: Nom de la classe
            properties: Dictionnaire des propriétés et valeurs
            instance_id: ID personnalisé (optionnel)
        
        Returns:
            str: ID de l'instance créée
        """
        try:
            # Trouve la classe
            class_uri = None
            for s, p, o in self.graph.triples((None, RDFS.label, Literal(class_name))):
                if (s, RDF.type, OWL.Class) in self.graph:
                    class_uri = s
                    break
            
            if not class_uri:
                return None
            
            # Génère un ID si non fourni
            if not instance_id:
                instance_id = f"{class_name.lower()}_{uuid.uuid4().hex[:8]}"
            
            # Crée l'instance
            instance_uri = URIRef(f"{self.ns['ex']}{instance_id}")
            self.graph.add((instance_uri, RDF.type, class_uri))
            
            # Ajoute les propriétés
            for prop_name, value in properties.items():
                prop_uri = URIRef(f"{self.ns['ex']}{prop_name}")
                
                # Vérifie si la propriété existe
                if (prop_uri, RDF.type, OWL.DatatypeProperty) in self.graph:
                    self.graph.add((instance_uri, prop_uri, Literal(value)))
                elif (prop_uri, RDF.type, OWL.ObjectProperty) in self.graph:
                    # Pour les ObjectProperty, on suppose que c'est une URI
                    if value.startswith('http'):
                        self.graph.add((instance_uri, prop_uri, URIRef(value)))
                    else:
                        self.graph.add((instance_uri, prop_uri, URIRef(f"{self.ns['ex']}{value}")))
            
            print(f"✅ Instance créée: {instance_id} de type {class_name}")
            return instance_id
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'instance: {e}")
            return None
    
    def create_instance(self, class_name: str, properties: dict, instance_id: str = None) -> str:
        """
        Crée une instance d'une classe (alias stable de create_instance_dynamically)
        Args:
            class_name: Nom de la classe
            properties: Dictionnaire des propriétés
            instance_id: ID personnalisé (optionnel)
        Returns:
            str: ID de l'instance créée
        """
        return self.create_instance_dynamically(class_name, properties, instance_id)
    
    def query_ontology_introspectively(self, query_type: str, **kwargs) -> List[Dict]:
        """
        Requête introspective de l'ontologie
        
        Args:
            query_type: Type de requête ('classes', 'properties', 'instances', 'structure')
            **kwargs: Paramètres spécifiques à la requête
        
        Returns:
            List[Dict]: Résultats de la requête
        """
        try:
            if query_type == 'classes':
                return self._query_classes(**kwargs)
            elif query_type == 'properties':
                return self._query_properties(**kwargs)
            elif query_type == 'instances':
                return self._query_instances(**kwargs)
            elif query_type == 'structure':
                return self._query_structure(**kwargs)
            else:
                return []
                
        except Exception as e:
            print(f"❌ Erreur lors de la requête introspective: {e}")
            return []
    
    def _query_classes(self, **kwargs) -> List[Dict]:
        """Requête les classes de l'ontologie"""
        classes = []
        for s, p, o in self.graph.triples((None, RDF.type, OWL.Class)):
            class_info = {
                'uri': str(s),
                'name': str(s).split('/')[-1],
                'label': self._get_label(s),
                'instances_count': len(list(self.graph.triples((None, RDF.type, s))))
            }
            classes.append(class_info)
        return classes
    
    def _query_properties(self, **kwargs) -> List[Dict]:
        """Requête les propriétés de l'ontologie"""
        properties = []
        for s, p, o in self.graph.triples((None, RDF.type, OWL.DatatypeProperty)):
            prop_info = {
                'uri': str(s),
                'name': str(s).split('/')[-1],
                'label': self._get_label(s),
                'type': 'DatatypeProperty',
                'range': self._get_property_range(s)
            }
            properties.append(prop_info)
        
        for s, p, o in self.graph.triples((None, RDF.type, OWL.ObjectProperty)):
            prop_info = {
                'uri': str(s),
                'name': str(s).split('/')[-1],
                'label': self._get_label(s),
                'type': 'ObjectProperty',
                'range': self._get_property_range(s)
            }
            properties.append(prop_info)
        
        return properties
    
    def _query_instances(self, class_name: str = None, **kwargs) -> List[Dict]:
        """Requête les instances de l'ontologie"""
        instances = []
        
        if class_name:
            # Instances d'une classe spécifique
            class_uri = None
            for s, p, o in self.graph.triples((None, RDFS.label, Literal(class_name))):
                if (s, RDF.type, OWL.Class) in self.graph:
                    class_uri = s
                    break
            
            if class_uri:
                for s, p, o in self.graph.triples((None, RDF.type, class_uri)):
                    instance_info = {
                        'uri': str(s),
                        'id': str(s).split('/')[-1],
                        'class': class_name,
                        'properties': self._get_instance_properties(s)
                    }
                    instances.append(instance_info)
        else:
            # Toutes les instances
            for s, p, o in self.graph.triples((None, RDF.type, OWL.Class)):
                class_name = str(s).split('/')[-1]
                for instance, type_p, type_o in self.graph.triples((None, RDF.type, s)):
                    instance_info = {
                        'uri': str(instance),
                        'id': str(instance).split('/')[-1],
                        'class': class_name,
                        'properties': self._get_instance_properties(instance)
                    }
                    instances.append(instance_info)
        
        return instances
    
    def _query_structure(self, **kwargs) -> Dict:
        """Requête la structure complète de l'ontologie"""
        return self.introspect_ontology()
    
    def add_behavior_class(self, class_name: str, methods: List[Dict]) -> bool:
        """
        Ajoute une classe avec des comportements (méthodes)
        
        Args:
            class_name: Nom de la classe
            methods: Liste des méthodes avec leurs paramètres et types de retour
        
        Returns:
            bool: True si succès
        """
        try:
            # Crée la classe principale
            class_uri = URIRef(f"{self.ns['ex']}{class_name}")
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(class_name)))
            
            # Crée la classe de comportement associée
            behavior_class_uri = URIRef(f"{self.ns['ex']}{class_name}Behavior")
            self.graph.add((behavior_class_uri, RDF.type, OWL.Class))
            self.graph.add((behavior_class_uri, RDFS.label, Literal(f"{class_name}Behavior")))
            
            # Lien entre la classe et son comportement
            self.graph.add((class_uri, self.ns['ex'].hasBehavior, behavior_class_uri))
            
            # Ajoute les méthodes
            for method in methods:
                method_uri = URIRef(f"{self.ns['ex']}{method['name']}")
                self.graph.add((method_uri, RDF.type, OWL.ObjectProperty))
                self.graph.add((method_uri, RDFS.label, Literal(method['name'])))
                self.graph.add((method_uri, RDFS.domain, behavior_class_uri))
                
                if 'return_type' in method:
                    return_type_uri = URIRef(f"{self.ns['ex']}{method['return_type']}")
                    self.graph.add((method_uri, RDFS.range, return_type_uri))
                
                # Paramètres de la méthode
                if 'parameters' in method:
                    for param in method['parameters']:
                        param_uri = URIRef(f"{self.ns['ex']}{method['name']}_{param['name']}")
                        self.graph.add((param_uri, RDF.type, OWL.DatatypeProperty))
                        self.graph.add((param_uri, RDFS.label, Literal(param['name'])))
                        self.graph.add((param_uri, RDFS.domain, method_uri))
                        self.graph.add((param_uri, RDFS.range, XSD.string))
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de la classe comportementale: {e}")
            return False
    
    def add_state_machine(self, class_name: str, states: List[str], 
                         transitions: List[Dict]) -> bool:
        """
        Ajoute une machine à états pour une classe
        
        Args:
            class_name: Nom de la classe
            states: Liste des états possibles
            transitions: Liste des transitions (from_state, to_state, trigger)
        
        Returns:
            bool: True si succès
        """
        try:
            # Crée la machine à états
            sm_uri = URIRef(f"{self.ns['ex']}{class_name}StateMachine")
            self.graph.add((sm_uri, RDF.type, OWL.Class))
            self.graph.add((sm_uri, RDFS.label, Literal(f"{class_name}StateMachine")))
            
            # Lien avec la classe
            class_uri = URIRef(f"{self.ns['ex']}{class_name}")
            self.graph.add((class_uri, self.ns['ex'].hasStateMachine, sm_uri))
            
            # Ajoute les états
            for state in states:
                state_uri = URIRef(f"{self.ns['ex']}{class_name}_{state}")
                self.graph.add((state_uri, RDF.type, sm_uri))
                self.graph.add((state_uri, RDFS.label, Literal(state)))
            
            # Ajoute les transitions
            for trans in transitions:
                trans_uri = URIRef(f"{self.ns['ex']}{class_name}_{trans['from']}_to_{trans['to']}")
                self.graph.add((trans_uri, RDF.type, OWL.ObjectProperty))
                self.graph.add((trans_uri, RDFS.label, Literal(f"{trans['from']} -> {trans['to']}")))
                self.graph.add((trans_uri, RDFS.domain, URIRef(f"{self.ns['ex']}{class_name}_{trans['from']}")))
                self.graph.add((trans_uri, RDFS.range, URIRef(f"{self.ns['ex']}{class_name}_{trans['to']}")))
                
                if 'trigger' in trans:
                    self.graph.add((trans_uri, self.ns['ex'].hasTrigger, Literal(trans['trigger'])))
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de la machine à états: {e}")
            return False
    
    def class_exists(self, class_uri: str) -> bool:
        """Vérifie si une classe existe dans l'ontologie"""
        return (URIRef(class_uri), RDF.type, OWL.Class) in self.graph
    
    def get_instance_property(self, instance_id: str, property_name: str) -> any:
        """Récupère une propriété d'une instance"""
        try:
            # Trouve l'instance dans tous les namespaces
            for prefix, namespace in self.ns.items():
                if prefix in ['client', 'product', 'order', 'instance']:
                    instance_uri = URIRef(f"{namespace}{instance_id}")
                    property_uri = URIRef(f"{self.ns['ex']}{property_name}")
                    
                    for s, p, o in self.graph.triples((instance_uri, property_uri, None)):
                        return str(o)
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de la propriété: {e}")
            return None
    
    def update_instance_property(self, instance_id: str, property_name: str, value: any) -> bool:
        """Met à jour une propriété d'une instance"""
        try:
            # Trouve l'instance dans tous les namespaces
            for prefix, namespace in self.ns.items():
                if prefix in ['client', 'product', 'order', 'instance']:
                    instance_uri = URIRef(f"{namespace}{instance_id}")
                    property_uri = URIRef(f"{self.ns['ex']}{property_name}")
                    
                    # Supprime l'ancienne valeur
                    for s, p, o in self.graph.triples((instance_uri, property_uri, None)):
                        self.graph.remove((s, p, o))
                    
                    # Ajoute la nouvelle valeur
                    self.graph.add((instance_uri, property_uri, Literal(value)))
                    return True
            
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour de la propriété: {e}")
            return False
    
    def add_business_handler(self, intent_name: str, handler_config: Dict) -> bool:
        """
        Ajoute un handler métier déclaratif dans l'ontologie
        
        Args:
            intent_name: Nom de l'intention (ex: 'create_order')
            handler_config: Configuration du handler
                {
                    'description': 'Description du handler',
                    'extraction_patterns': {
                        'client_name': [r'pour\s+([a-zA-Z\s]+)', r'client\s+([a-zA-Z\s]+)'],
                        'products': [r'(\d+)\s+unités?\s+de\s+([a-zA-Z\s]+)']
                    },
                    'workflow': [
                        {'step': 1, 'action': 'validate_client', 'params': ['client_name']},
                        {'step': 2, 'action': 'check_stock', 'params': ['products']},
                        {'step': 3, 'action': 'create_order', 'params': ['client_name', 'products']},
                        {'step': 4, 'action': 'process_payment', 'params': ['order_id', 'amount']}
                    ],
                    'rules': [
                        {'condition': 'stock_insufficient', 'action': 'suggest_alternatives'},
                        {'condition': 'payment_failed', 'action': 'retry_payment'}
                    ]
                }
        
        Returns:
            bool: True si succès
        """
        try:
            ex = self.ns['ex']
            
            # Crée l'URI du handler
            handler_uri = URIRef(f"{ex}Handler_{intent_name}")
            
            # Ajoute la classe Handler si elle n'existe pas
            if not (ex.Handler, RDF.type, OWL.Class) in self.graph:
                self.graph.add((ex.Handler, RDF.type, OWL.Class))
                self.graph.add((ex.Handler, RDFS.label, Literal("BusinessHandler")))
            
            # Crée l'instance du handler
            self.graph.add((handler_uri, RDF.type, ex.Handler))
            self.graph.add((handler_uri, RDFS.label, Literal(f"Handler_{intent_name}")))
            self.graph.add((handler_uri, ex.hasIntent, Literal(intent_name)))
            
            # Ajoute la description
            if 'description' in handler_config:
                self.graph.add((handler_uri, ex.hasDescription, 
                               Literal(handler_config['description'])))
            
            # Ajoute les patterns d'extraction
            if 'extraction_patterns' in handler_config:
                patterns_uri = URIRef(f"{ex}Patterns_{intent_name}")
                self.graph.add((handler_uri, ex.hasExtractionPatterns, patterns_uri))
                self.graph.add((patterns_uri, RDF.type, ex.ExtractionPatterns))
                
                for param_name, patterns in handler_config['extraction_patterns'].items():
                    param_uri = URIRef(f"{ex}Param_{intent_name}_{param_name}")
                    self.graph.add((patterns_uri, ex.hasParameter, param_uri))
                    self.graph.add((param_uri, ex.hasName, Literal(param_name)))
                    
                    for i, pattern in enumerate(patterns):
                        pattern_uri = URIRef(f"{ex}Pattern_{intent_name}_{param_name}_{i}")
                        self.graph.add((param_uri, ex.hasPattern, pattern_uri))
                        self.graph.add((pattern_uri, ex.hasRegex, Literal(pattern)))
            
            # Ajoute le workflow d'exécution
            if 'workflow' in handler_config:
                workflow_uri = URIRef(f"{ex}Workflow_{intent_name}")
                self.graph.add((handler_uri, ex.hasWorkflow, workflow_uri))
                self.graph.add((workflow_uri, RDF.type, ex.Workflow))
                
                for step in handler_config['workflow']:
                    step_uri = URIRef(f"{ex}Step_{intent_name}_{step['step']}")
                    self.graph.add((workflow_uri, ex.hasStep, step_uri))
                    self.graph.add((step_uri, RDF.type, ex.WorkflowStep))
                    self.graph.add((step_uri, ex.hasStepNumber, Literal(step['step'])))
                    self.graph.add((step_uri, ex.hasAction, Literal(step['action'])))
                    
                    for param in step.get('params', []):
                        self.graph.add((step_uri, ex.hasParameter, Literal(param)))
            
            # Ajoute les règles métier
            if 'rules' in handler_config:
                rules_uri = URIRef(f"{ex}Rules_{intent_name}")
                self.graph.add((handler_uri, ex.hasRules, rules_uri))
                self.graph.add((rules_uri, RDF.type, ex.BusinessRules))
                
                for i, rule in enumerate(handler_config['rules']):
                    rule_uri = URIRef(f"{ex}Rule_{intent_name}_{i}")
                    self.graph.add((rules_uri, ex.hasRule, rule_uri))
                    self.graph.add((rule_uri, RDF.type, ex.BusinessRule))
                    self.graph.add((rule_uri, ex.hasCondition, Literal(rule['condition'])))
                    self.graph.add((rule_uri, ex.hasAction, Literal(rule['action'])))
            
            print(f"✅ Handler métier '{intent_name}' ajouté à l'ontologie")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout du handler métier: {e}")
            return False
    
    def get_business_handler(self, intent_name: str) -> Optional[Dict]:
        """
        Récupère la configuration d'un handler métier depuis l'ontologie
        
        Args:
            intent_name: Nom de l'intention
        
        Returns:
            Optional[Dict]: Configuration du handler ou None
        """
        try:
            ex = self.ns['ex']
            handler_uri = URIRef(f"{ex}Handler_{intent_name}")
            
            if not (handler_uri, RDF.type, ex.Handler) in self.graph:
                return None
            
            config = {
                'intent_name': intent_name,
                'extraction_patterns': {},
                'workflow': [],
                'rules': []
            }
            
            # Récupère la description
            for s, p, o in self.graph.triples((handler_uri, ex.hasDescription, None)):
                config['description'] = str(o)
            
            # Récupère les patterns d'extraction
            for s, p, patterns_uri in self.graph.triples((handler_uri, ex.hasExtractionPatterns, None)):
                for s2, p2, param_uri in self.graph.triples((patterns_uri, ex.hasParameter, None)):
                    param_name = None
                    patterns = []
                    
                    for s3, p3, o3 in self.graph.triples((param_uri, ex.hasName, None)):
                        param_name = str(o3)
                    
                    for s3, p3, pattern_uri in self.graph.triples((param_uri, ex.hasPattern, None)):
                        for s4, p4, o4 in self.graph.triples((pattern_uri, ex.hasRegex, None)):
                            patterns.append(str(o4))
                    
                    if param_name:
                        config['extraction_patterns'][param_name] = patterns
            
            # Récupère le workflow
            for s, p, workflow_uri in self.graph.triples((handler_uri, ex.hasWorkflow, None)):
                for s2, p2, step_uri in self.graph.triples((workflow_uri, ex.hasStep, None)):
                    step = {'params': []}
                    
                    for s3, p3, o3 in self.graph.triples((step_uri, None, None)):
                        if p3 == ex.hasStepNumber:
                            step['step'] = int(str(o3))
                        elif p3 == ex.hasAction:
                            step['action'] = str(o3)
                        elif p3 == ex.hasParameter:
                            step['params'].append(str(o3))
                    
                    if 'step' in step:
                        config['workflow'].append(step)
                
                # Trie le workflow par numéro d'étape
                config['workflow'].sort(key=lambda x: x['step'])
            
            # Récupère les règles
            for s, p, rules_uri in self.graph.triples((handler_uri, ex.hasRules, None)):
                for s2, p2, rule_uri in self.graph.triples((rules_uri, ex.hasRule, None)):
                    rule = {}
                    
                    for s3, p3, o3 in self.graph.triples((rule_uri, None, None)):
                        if p3 == ex.hasCondition:
                            rule['condition'] = str(o3)
                        elif p3 == ex.hasAction:
                            rule['action'] = str(o3)
                    
                    if 'condition' in rule and 'action' in rule:
                        config['rules'].append(rule)
            
            return config
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du handler: {e}")
            return None
    
    def list_business_handlers(self) -> List[Dict]:
        """
        Liste tous les handlers métiers disponibles
        
        Returns:
            List[Dict]: Liste des handlers avec leurs descriptions
        """
        try:
            ex = self.ns['ex']
            handlers = []
            
            for s, p, o in self.graph.triples((None, RDF.type, ex.Handler)):
                handler_info = {}
                
                # Récupère le nom de l'intention
                for s2, p2, o2 in self.graph.triples((s, ex.hasIntent, None)):
                    handler_info['intent_name'] = str(o2)
                
                # Récupère la description
                for s2, p2, o2 in self.graph.triples((s, ex.hasDescription, None)):
                    handler_info['description'] = str(o2)
                
                if 'intent_name' in handler_info:
                    handlers.append(handler_info)
            
            return handlers
            
        except Exception as e:
            print(f"❌ Erreur lors de la liste des handlers: {e}")
            return []
    
    def execute_business_workflow(self, intent_name: str, params: Dict, 
                                 tools_manager=None) -> Tuple[bool, str]:
        """
        Exécute le workflow métier d'une intention
        
        Args:
            intent_name: Nom de l'intention
            params: Paramètres extraits
            tools_manager: Gestionnaire d'outils (optionnel)
        
        Returns:
            Tuple[bool, str]: (succès, résultat)
        """
        try:
            # Récupère la configuration du handler
            handler_config = self.get_business_handler(intent_name)
            if not handler_config:
                return False, f"Handler métier '{intent_name}' non trouvé"
            
            print(f"🔄 Exécution du workflow métier pour '{intent_name}'")
            print(f"   Étapes: {len(handler_config.get('workflow', []))}")
            
            # Exécute chaque étape du workflow
            workflow_results = {}
            for step in handler_config.get('workflow', []):
                step_num = step['step']
                action = step['action']
                step_params = step.get('params', [])
                
                print(f"   Étape {step_num}: {action}")
                
                # Prépare les paramètres pour cette étape
                action_params = {}
                for param_name in step_params:
                    if param_name in params:
                        action_params[param_name] = params[param_name]
                    elif param_name in workflow_results:
                        action_params[param_name] = workflow_results[param_name]
                
                # Exécute l'action
                if tools_manager and hasattr(tools_manager, action):
                    action_method = getattr(tools_manager, action)
                    result = action_method(**action_params)
                    workflow_results[f"step_{step_num}_result"] = result
                    print(f"     ✅ Résultat: {result}")
                else:
                    # Action simulée si pas de gestionnaire d'outils
                    result = f"Action '{action}' simulée avec paramètres: {action_params}"
                    workflow_results[f"step_{step_num}_result"] = result
                    print(f"     ⚠️ Action simulée: {action}")
            
            # Applique les règles métier
            for rule in handler_config.get('rules', []):
                condition = rule['condition']
                action = rule['action']
                
                # Logique simplifiée pour les conditions
                if condition == 'stock_insufficient' and 'stock_error' in str(workflow_results):
                    print(f"   🔄 Règle déclenchée: {condition} -> {action}")
                    # Ici on pourrait exécuter l'action de la règle
            
            return True, f"Workflow exécuté avec succès. {len(workflow_results)} résultats générés."
            
        except Exception as e:
            return False, f"Erreur lors de l'exécution du workflow: {e}"

    def search_semantic(self, query_text: str, top_k: int = 5, 
                       search_type: str = "all") -> List[Dict]:
        """
        Recherche sémantique dans la base de connaissances
        
        Args:
            query_text: Texte de recherche
            top_k: Nombre maximum de résultats
            search_type: Type de recherche ('all', 'clients', 'products', 'orders')
        
        Returns:
            List[Dict]: Résultats de recherche
        """
        try:
            results = []
            
            # Recherche dans le vector store
            vector_results = self.vector_store.search(query_text, top_k)
            
            # Recherche dans l'ontologie
            ontology_results = []
            
            if search_type in ['all', 'clients']:
                # Recherche dans les clients
                clients = self.get_clients()
                for client in clients:
                    if (query_text.lower() in client['name'].lower() or 
                        query_text.lower() in client['email'].lower()):
                        ontology_results.append({
                            'type': 'client',
                            'id': client['id'],
                            'name': client['name'],
                            'email': client['email'],
                            'score': 0.8
                        })
            
            if search_type in ['all', 'products']:
                # Recherche dans les produits
                products_query = f"""
                SELECT ?product ?name ?price ?stock ?description
                WHERE {{
                    ?product rdf:type <{self.ns['ex']}Product> .
                    ?product <{self.ns['ex']}hasName> ?name .
                    ?product <{self.ns['ex']}hasPrice> ?price .
                    ?product <{self.ns['ex']}hasStock> ?stock .
                    ?product <{self.ns['ex']}hasDescription> ?description .
                }}
                """
                products_results = self.query_graph(products_query)
                for result in products_results:
                    product_name = result.get('name', '')
                    if query_text.lower() in product_name.lower():
                        ontology_results.append({
                            'type': 'product',
                            'id': str(result['product']).split('/')[-1],
                            'name': product_name,
                            'price': result.get('price', 0),
                            'stock': result.get('stock', 0),
                            'description': result.get('description', ''),
                            'score': 0.7
                        })
            
            # Combiner et trier les résultats
            all_results = vector_results + ontology_results
            all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return all_results[:top_k]
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche sémantique: {e}")
            return []

    def add_entity(self, entity_name: str, entity_data: Dict) -> bool:
        """Ajoute une entité générique à la base de connaissances"""
        try:
            # Créer un URI unique pour l'entité
            entity_uri = URIRef(f"{self.ns['ex']}{entity_name}")
            
            # Ajouter le type d'entité
            self.graph.add((entity_uri, RDF.type, OWL.NamedIndividual))
            self.graph.add((entity_uri, RDFS.label, Literal(entity_name)))
            
            # Ajouter les propriétés de l'entité
            for key, value in entity_data.items():
                if key != 'name':  # Éviter la duplication du nom
                    if isinstance(value, dict):
                        # Pour les objets complexes, les sérialiser en JSON
                        import json
                        value = json.dumps(value)
                    elif isinstance(value, list):
                        # Pour les listes, les sérialiser en JSON
                        import json
                        value = json.dumps(value)
                    
                    # Créer une propriété pour cette clé
                    prop_uri = URIRef(f"{self.ns['ex']}has{key.capitalize()}")
                    self.graph.add((entity_uri, prop_uri, Literal(str(value))))
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'ajout de l'entité {entity_name}: {e}")
            return False
    
    def get_all_entities(self) -> Dict[str, Dict]:
        """Récupère toutes les entités de la base de connaissances"""
        try:
            entities = {}
            
            # Récupérer toutes les instances individuelles
            for subject, predicate, obj in self.graph.triples((None, RDF.type, OWL.NamedIndividual)):
                entity_name = str(subject).split('/')[-1]  # Extraire le nom de l'URI
                entity_data = {
                    'uri': str(subject),
                    'name': entity_name,
                    'properties': {}
                }
                
                # Récupérer toutes les propriétés de cette entité
                for s, p, o in self.graph.triples((subject, None, None)):
                    if p != RDF.type:  # Exclure le type
                        prop_name = str(p).split('/')[-1]  # Extraire le nom de la propriété
                        prop_value = str(o)
                        
                        # Essayer de désérialiser les valeurs JSON
                        try:
                            import json
                            if prop_value.startswith('{') or prop_value.startswith('['):
                                prop_value = json.loads(prop_value)
                        except:
                            pass  # Garder la valeur originale si ce n'est pas du JSON
                        
                        entity_data['properties'][prop_name] = prop_value
                
                # Extraire les propriétés principales
                for prop_name, prop_value in entity_data['properties'].items():
                    if prop_name.lower().endswith('name'):
                        entity_data['name'] = prop_value
                    elif prop_name.lower().endswith('type'):
                        entity_data['type'] = prop_value
                    elif prop_name.lower().endswith('description'):
                        entity_data['description'] = prop_value
                    elif prop_name.lower().endswith('created_at'):
                        entity_data['created_at'] = prop_value
                    elif prop_name.lower().endswith('source'):
                        entity_data['source'] = prop_value
                    elif prop_name.lower().endswith('domain'):
                        entity_data['domain'] = prop_value
                
                entities[entity_name] = entity_data
            
            return entities
            
        except Exception as e:
            print(f"Erreur lors de la récupération des entités: {e}")
            return {}
    
    def get_entity(self, entity_name: str) -> Optional[Dict]:
        """Récupère une entité spécifique par son nom"""
        try:
            all_entities = self.get_all_entities()
            return all_entities.get(entity_name)
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'entité {entity_name}: {e}")
            return None


class SemanticProxy:
    """
    Proxy sémantique pour l'exécution dynamique de méthodes et l'instanciation réflexive
    Équivalent sémantique des Dynamic Proxy en POO
    """
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.proxy_cache = {}  # Cache des proxies créés
    
    def create_proxy(self, class_name: str, instance_id: str = None) -> 'SemanticProxyInstance':
        """
        Crée un proxy pour une classe ou une instance
        
        Args:
            class_name: Nom de la classe
            instance_id: ID de l'instance (optionnel)
        
        Returns:
            SemanticProxyInstance: Proxy pour l'objet
        """
        try:
            # Vérifie que la classe existe
            class_uri = f"{self.kb.ns['ex']}{class_name}"
            if not self.kb.class_exists(class_uri):
                raise ValueError(f"Classe '{class_name}' non trouvée")
            
            # Crée le proxy
            proxy = SemanticProxyInstance(self.kb, class_name, instance_id)
            
            # Cache le proxy
            cache_key = f"{class_name}:{instance_id}" if instance_id else class_name
            self.proxy_cache[cache_key] = proxy
            
            print(f"🔧 Proxy créé pour {class_name}" + (f" (instance: {instance_id})" if instance_id else ""))
            return proxy
            
        except Exception as e:
            print(f"❌ Erreur lors de la création du proxy: {e}")
            return None
    
    def get_proxy(self, class_name: str, instance_id: str = None) -> 'SemanticProxyInstance':
        """Récupère un proxy existant du cache"""
        cache_key = f"{class_name}:{instance_id}" if instance_id else class_name
        return self.proxy_cache.get(cache_key)
    
    def list_available_methods(self, class_name: str) -> List[Dict]:
        """
        Liste toutes les méthodes disponibles pour une classe
        
        Args:
            class_name: Nom de la classe
        
        Returns:
            List[Dict]: Liste des méthodes avec leurs signatures
        """
        try:
            methods = []
            class_uri = f"{self.kb.ns['ex']}{class_name}"
            
            # Recherche des méthodes dans l'ontologie
            for s, p, o in self.kb.graph.triples((None, RDFS.domain, URIRef(class_uri))):
                if (s, RDF.type, OWL.ObjectProperty) in self.kb.graph:
                    method_name = str(s).split('/')[-1]
                    
                    # Récupère les paramètres
                    parameters = []
                    for param_s, param_p, param_o in self.kb.graph.triples((s, None, None)):
                        if str(param_p).endswith('_param'):
                            param_name = str(param_o)
                            parameters.append({'name': param_name, 'type': 'string'})
                    
                    # Récupère le type de retour
                    return_type = None
                    for return_s, return_p, return_o in self.kb.graph.triples((s, RDFS.range, None)):
                        return_type = str(return_o).split('/')[-1]
                    
                    methods.append({
                        'name': method_name,
                        'parameters': parameters,
                        'return_type': return_type
                    })
            
            return methods
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des méthodes: {e}")
            return []
    
    def reflect_class_structure(self, class_name: str) -> Dict:
        """
        Réflexion complète sur la structure d'une classe
        
        Args:
            class_name: Nom de la classe
        
        Returns:
            Dict: Structure complète de la classe
        """
        try:
            class_uri = f"{self.kb.ns['ex']}{class_name}"
            
            # Propriétés de la classe
            properties = []
            for s, p, o in self.kb.graph.triples((URIRef(class_uri), None, None)):
                if p == RDFS.label:
                    continue
                prop_name = str(p).split('/')[-1]
                properties.append(prop_name)
            
            # Méthodes disponibles sur la classe principale
            methods = self.list_available_methods(class_name)
            
            # Ajoute les méthodes de la classe de comportement associée
            behavior_class_uri = f"{self.kb.ns['ex']}{class_name}Behavior"
            if (URIRef(behavior_class_uri), RDF.type, OWL.Class) in self.kb.graph:
                behavior_methods = self.list_available_methods(f"{class_name}Behavior")
                # Ajoute uniquement les méthodes qui ne sont pas déjà listées
                method_names = {m['name'] for m in methods}
                for m in behavior_methods:
                    if m['name'] not in method_names:
                        methods.append(m)
            
            # Instances existantes
            instances = self.kb.get_instances_of_class(class_uri)
            
            return {
                'class_name': class_name,
                'class_uri': class_uri,
                'properties': properties,
                'methods': methods,
                'instances_count': len(instances),
                'instances': [str(uri).split('/')[-1] for uri in instances]
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la réflexion: {e}")
            return {}


class SemanticProxyInstance:
    """
    Instance de proxy sémantique pour un objet spécifique
    Permet l'exécution dynamique de méthodes
    """
    
    def __init__(self, knowledge_base, class_name: str, instance_id: str = None):
        self.kb = knowledge_base
        self.class_name = class_name
        self.instance_id = instance_id
        self.class_uri = f"{knowledge_base.ns['ex']}{class_name}"
        
        if instance_id:
            self.instance_uri = f"{knowledge_base.ns['instance']}{instance_id}"
        else:
            self.instance_uri = None
    
    def __getattr__(self, method_name: str):
        """
        Intercepte les appels de méthodes et les exécute dynamiquement
        Équivalent de __getattr__ en Python pour la réflexion
        """
        def dynamic_method(*args, **kwargs):
            return self._execute_method(method_name, *args, **kwargs)
        return dynamic_method
    
    def _execute_method(self, method_name: str, *args, **kwargs) -> any:
        """
        Exécute une méthode par réflexion
        
        Args:
            method_name: Nom de la méthode
            *args: Arguments positionnels
            **kwargs: Arguments nommés
        
        Returns:
            any: Résultat de l'exécution
        """
        try:
            print(f"🔄 Exécution réflexive: {self.class_name}.{method_name}")
            print(f"   Instance: {self.instance_id}")
            print(f"   Arguments: {args}")
            print(f"   Paramètres nommés: {kwargs}")
            
            # Vérifie que la méthode existe sur la classe principale ou comportement
            method_uri = f"{self.kb.ns['ex']}{method_name}"
            if not self._method_exists(method_uri):
                raise AttributeError(f"Méthode '{method_name}' non trouvée dans la classe '{self.class_name}' ni dans '{self.class_name}Behavior'")
            
            # Exécute la logique selon la méthode
            if method_name == "passer_commande":
                return self._execute_passer_commande(*args, **kwargs)
            elif method_name == "payer":
                return self._execute_payer(*args, **kwargs)
            elif method_name == "modifier_profil":
                return self._execute_modifier_profil(*args, **kwargs)
            elif method_name == "changer_etat":
                return self._execute_changer_etat(*args, **kwargs)
            else:
                # Méthode générique
                return self._execute_generic_method(method_name, *args, **kwargs)
                
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de {method_name}: {e}")
            return None
    
    def _method_exists(self, method_uri: str) -> bool:
        """Vérifie si une méthode existe dans l'ontologie (classe principale ou comportement)"""
        # Sur la classe principale
        if (URIRef(method_uri), RDFS.domain, URIRef(self.class_uri)) in self.kb.graph:
            return True
        # Sur la classe de comportement associée
        behavior_class_uri = f"{self.kb.ns['ex']}{self.class_name}Behavior"
        if (URIRef(method_uri), RDFS.domain, URIRef(behavior_class_uri)) in self.kb.graph:
            return True
        return False
    
    def _execute_passer_commande(self, *args, **kwargs):
        """Exécute la méthode passer_commande"""
        produits = kwargs.get('produits', args[0] if args else [])
        quantite = kwargs.get('quantite', args[1] if len(args) > 1 else 1)
        
        # Simulation de création de commande
        import uuid
        order_id = f"order_{uuid.uuid4().hex[:8]}"
        
        # Ajoute la commande dans l'ontologie
        self.kb.add_order(order_id, self.instance_id, 0.0, "en_attente")
        
        print(f"   ✅ Commande créée: {order_id}")
        return order_id
    
    def _execute_payer(self, *args, **kwargs):
        """Exécute la méthode payer"""
        montant = kwargs.get('montant', args[0] if args else 0)
        methode = kwargs.get('methode', args[1] if len(args) > 1 else 'carte')
        
        # Simulation de paiement
        import uuid
        payment_id = f"payment_{uuid.uuid4().hex[:8]}"
        
        print(f"   ✅ Paiement de {montant}€ par {methode}: {payment_id}")
        return payment_id
    
    def _execute_modifier_profil(self, *args, **kwargs):
        """Exécute la méthode modifier_profil"""
        nouveau_nom = kwargs.get('nouveau_nom', args[0] if args else None)
        nouveau_email = kwargs.get('nouveau_email', args[1] if len(args) > 1 else None)
        
        # Met à jour l'instance dans l'ontologie
        if nouveau_nom:
            self.kb.update_instance_property(self.instance_id, 'hasName', nouveau_nom)
        if nouveau_email:
            self.kb.update_instance_property(self.instance_id, 'hasEmail', nouveau_email)
        
        print(f"   ✅ Profil modifié: {nouveau_nom}, {nouveau_email}")
        return self.instance_id
    
    def _execute_changer_etat(self, *args, **kwargs):
        """Exécute la méthode changer_etat"""
        nouvel_etat = kwargs.get('nouvel_etat', args[0] if args else 'inconnu')
        
        # Met à jour l'état dans l'ontologie
        self.kb.update_instance_property(self.instance_id, 'hasStatus', nouvel_etat)
        
        print(f"   ✅ État changé vers: {nouvel_etat}")
        return nouvel_etat
    
    def _execute_generic_method(self, method_name: str, *args, **kwargs):
        """Exécute une méthode générique"""
        print(f"   🔧 Méthode générique '{method_name}' exécutée")
        return f"Résultat de {method_name}"
    
    def get_property(self, property_name: str) -> any:
        """Récupère une propriété de l'instance"""
        if not self.instance_id:
            raise ValueError("Pas d'instance associée à ce proxy")
        
        return self.kb.get_instance_property(self.instance_id, property_name)
    
    def set_property(self, property_name: str, value: any) -> bool:
        """Définit une propriété de l'instance"""
        if not self.instance_id:
            raise ValueError("Pas d'instance associée à ce proxy")
        
        return self.kb.update_instance_property(self.instance_id, property_name, value)
    
    def get_methods(self) -> List[Dict]:
        """Récupère la liste des méthodes disponibles pour cette instance"""
        return self.kb.list_available_methods(self.class_name)
    
    def __str__(self):
        return f"SemanticProxyInstance({self.class_name}:{self.instance_id})"
    
    def __repr__(self):
        return self.__str__()