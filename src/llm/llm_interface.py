"""
Interface avec un vrai LLM (OpenAI)
Gère l'extraction d'intentions, de paramètres et la génération d'embeddings
"""

import os
import json
import openai
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

class LLMInterface:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialise l'interface LLM
        
        Args:
            api_key: Clé API OpenAI (optionnel, peut être dans .env)
            model: Modèle à utiliser
        """
        self.model = model
        
        # Configuration de l'API
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("Clé API OpenAI manquante. Définissez OPENAI_API_KEY dans .env ou passez-la en paramètre.")
            self.client = openai.OpenAI(api_key=api_key)
        
        # Prompts système pour l'extraction d'intentions et paramètres
        self.intent_extraction_prompt = """
Tu es un assistant spécialisé dans l'analyse de requêtes utilisateur pour un système de gestion de commandes.

Analyse la requête utilisateur et extrait l'intention principale et les paramètres pertinents.

Intentions possibles :
- create_order : Création d'une nouvelle commande
- validate_order : Validation d'une commande existante
- recommend_products : Recommandation de produits
- check_status : Vérification de statut ou historique
- process_payment : Traitement de paiement
- add_client : Ajout d'un nouveau client
- list_clients : Liste de tous les clients
- introspect_ontology : Introspection de la structure de l'ontologie
- extend_ontology : Extension dynamique de l'ontologie avec une nouvelle classe
- create_instance : Création dynamique d'une instance d'une classe
- query_ontology : Requête introspective sur l'ontologie

Paramètres à extraire selon l'intention :
- create_order : client_name, products (liste avec product_name et quantity), immediate_payment
- validate_order : order_id
- recommend_products : query_text, reference_product
- check_status : order_id, client_name
- process_payment : order_id, amount
- add_client : client_name, email
- list_clients : (aucun paramètre)
- introspect_ontology : (aucun paramètre)
- extend_ontology : class_name, properties (liste avec name, type, label), namespace
- create_instance : class_name, properties (dictionnaire), instance_id
- query_ontology : query_type (classes, properties, instances, structure), class_name

Réponds uniquement avec un JSON valide au format :
{
    "intent": "intention_détectée",
    "confidence": 0.95,
    "parameters": {
        "param1": "valeur1",
        "param2": "valeur2"
    }
}
"""

        self.embedding_model = "text-embedding-3-small"
    
    def extract_intent_and_parameters(self, user_query: str) -> Tuple[str, Dict, float]:
        """
        Extrait l'intention et les paramètres d'une requête utilisateur
        
        Args:
            user_query: Requête utilisateur en langage naturel
        
        Returns:
            Tuple[str, Dict, float]: (intention, paramètres, confiance)
        """
        try:
            # Construction du prompt
            messages = [
                {"role": "system", "content": self.intent_extraction_prompt},
                {"role": "user", "content": f"Requête utilisateur : {user_query}"}
            ]
            
            # Appel à l'API avec la nouvelle syntaxe
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,  # Faible température pour plus de cohérence
                max_tokens=500
            )
            
            # Parsing de la réponse JSON
            content = response.choices[0].message.content.strip()
            
            # Nettoyage du JSON (suppression de markdown si présent)
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            result = json.loads(content)
            
            intent = result.get("intent", "unknown")
            parameters = result.get("parameters", {})
            confidence = result.get("confidence", 0.0)
            
            print(f"🤖 LLM - Intention extraite: {intent} (confiance: {confidence:.2f})")
            print(f"🤖 LLM - Paramètres: {parameters}")
            
            return intent, parameters, confidence
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de parsing JSON: {e}")
            print(f"Contenu reçu: {content}")
            return "unknown", {}, 0.0
            
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction d'intention: {e}")
            return "unknown", {}, 0.0
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Génère un embedding réel pour un texte donné
        
        Args:
            text: Texte à encoder
        
        Returns:
            List[float]: Vecteur d'embedding
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response.data[0].embedding
            print(f"🤖 LLM - Embedding généré pour: '{text[:50]}...'")
            
            return embedding
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération d'embedding: {e}")
            # Fallback vers un embedding simulé
            return self._generate_fallback_embedding(text)
    
    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """
        Génère un embedding de fallback (simulé) en cas d'erreur
        
        Args:
            text: Texte à encoder
        
        Returns:
            List[float]: Vecteur d'embedding simulé
        """
        import hashlib
        
        # Utilise un hash du texte pour générer un vecteur déterministe
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convertit les bytes en liste de floats entre -1 et 1
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            while len(chunk) < 4:
                chunk += b'\x00'
            
            value = int.from_bytes(chunk, byteorder='big')
            normalized_value = (value / (2**32 - 1)) * 2 - 1
            embedding.append(normalized_value)
        
        # S'assure d'avoir une dimension fixe (1536 pour text-embedding-3-small)
        while len(embedding) < 1536:
            remaining = 1536 - len(embedding)
            embedding.extend(embedding[:min(remaining, len(embedding))])
        
        return embedding[:1536]
    
    def get_recommendation_prompt(self, query_text: str, available_products: List[Dict]) -> str:
        """
        Génère un prompt pour les recommandations de produits
        
        Args:
            query_text: Description du besoin utilisateur
            available_products: Liste des produits disponibles
        
        Returns:
            str: Prompt pour le LLM
        """
        products_info = []
        for product in available_products:
            products_info.append(f"- {product['name']}: {product['description']} ({product['price']}€)")
        
        prompt = f"""
Tu es un assistant spécialisé dans les recommandations de produits informatiques.

L'utilisateur recherche : "{query_text}"

Produits disponibles :
{chr(10).join(products_info)}

Recommandes 3 produits maximum qui correspondent le mieux au besoin de l'utilisateur.
Pour chaque recommandation, explique brièvement pourquoi ce produit est pertinent.

Réponds au format :
1. **Nom du produit** - Prix€
   Raison de la recommandation

2. **Nom du produit** - Prix€
   Raison de la recommandation

3. **Nom du produit** - Prix€
   Raison de la recommandation
"""
        return prompt
    
    def get_product_recommendations(self, query_text: str, available_products: List[Dict]) -> str:
        """
        Génère des recommandations de produits via le LLM
        
        Args:
            query_text: Description du besoin utilisateur
            available_products: Liste des produits disponibles
        
        Returns:
            str: Recommandations formatées
        """
        try:
            prompt = self.get_recommendation_prompt(query_text, available_products)
            
            messages = [
                {"role": "system", "content": "Tu es un expert en produits informatiques."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            recommendations = response.choices[0].message.content.strip()
            print(f"🤖 LLM - Recommandations générées pour: '{query_text}'")
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération de recommandations: {e}")
            return "❌ Impossible de générer des recommandations pour le moment."
    
    def get_error_explanation(self, error_type: str, context: str) -> str:
        """
        Génère une explication d'erreur en langage naturel
        
        Args:
            error_type: Type d'erreur
            context: Contexte de l'erreur
        
        Returns:
            str: Explication de l'erreur
        """
        try:
            prompt = f"""
Tu es un assistant spécialisé dans l'explication d'erreurs techniques.

Type d'erreur: {error_type}
Contexte: {context}

Explique cette erreur de manière claire et propose des solutions possibles.
Réponds en français de manière concise et utile.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un assistant technique utile."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Erreur lors de la génération d'explication: {e}"
    
    def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Génère une réponse textuelle avec l'LLM
        
        Args:
            prompt: Prompt à envoyer à l'LLM
            temperature: Contrôle la créativité (0.0 = déterministe, 1.0 = très créatif)
            max_tokens: Nombre maximum de tokens dans la réponse
        
        Returns:
            str: Réponse générée par l'LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un assistant métier intelligent et utile."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération de réponse: {e}")
            return f"Désolé, je n'ai pas pu générer une réponse. Erreur: {e}" 