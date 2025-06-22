"""
Module de gestion de la base vectorielle
Utilise chromadb pour stocker et rechercher des embeddings de produits
"""

import chromadb
from typing import List, Dict, Optional
import hashlib


class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db", llm_interface=None):
        """Initialise la base vectorielle avec ChromaDB"""
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Interface LLM pour les vrais embeddings
        self.llm_interface = llm_interface
        
        # Détermine la dimension d'embedding à utiliser
        self.embedding_dimension = 1536 if llm_interface else 384
        
        # Vérifie si la collection existe et a la bonne dimension
        try:
            existing_collection = self.client.get_collection(name="products")
            # Teste la dimension en ajoutant un embedding temporaire
            test_embedding = [0.0] * self.embedding_dimension
            existing_collection.add(
                ids=["test"],
                embeddings=[test_embedding],
                documents=["test"],
                metadatas=[{"test": True}]
            )
            existing_collection.delete(ids=["test"])
            self.collection = existing_collection
        except Exception:
            # Supprime la collection existante si elle a une mauvaise dimension
            try:
                self.client.delete_collection(name="products")
            except:
                pass
            
            # Crée une nouvelle collection
            self.collection = self.client.create_collection(
                name="products",
                metadata={"description": "Collection des embeddings de produits"}
            )
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Génère un embedding pour un texte donné
        Utilise un vrai LLM si disponible, sinon un embedding simulé
        """
        if self.llm_interface:
            # Utilise le vrai LLM pour générer l'embedding
            return self.llm_interface.generate_embedding(text)
        else:
            # Fallback vers l'embedding simulé
            return self._generate_mock_embedding(text)
    
    def _generate_mock_embedding(self, text: str) -> List[float]:
        """
        Génère un embedding simulé pour un texte donné
        Dans un système réel, cette fonction utiliserait un modèle d'embedding
        comme sentence-transformers ou une API comme OpenAI
        """
        # Utilise un hash du texte pour générer un vecteur déterministe
        # mais pseudo-aléatoire pour simuler un embedding
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convertit les bytes en liste de floats entre -1 et 1
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            # Complète avec des zéros si nécessaire
            while len(chunk) < 4:
                chunk += b'\x00'
            
            # Convertit en float normalisé
            value = int.from_bytes(chunk, byteorder='big')
            normalized_value = (value / (2**32 - 1)) * 2 - 1  # Range [-1, 1]
            embedding.append(normalized_value)
        
        # S'assure d'avoir la dimension correcte
        while len(embedding) < self.embedding_dimension:
            remaining = self.embedding_dimension - len(embedding)
            embedding.extend(embedding[:min(remaining, len(embedding))])
        
        return embedding[:self.embedding_dimension]
    
    def add_product_embedding(self, product_id: str, description_text: str, 
                            vector_data: Optional[List[float]] = None) -> bool:
        """
        Ajoute un embedding de produit à la base vectorielle
        
        Args:
            product_id: Identifiant unique du produit
            description_text: Description textuelle du produit
            vector_data: Vecteur d'embedding (optionnel, généré automatiquement si None)
        
        Returns:
            bool: True si l'ajout a réussi
        """
        try:
            # Génère l'embedding si non fourni
            if vector_data is None:
                vector_data = self.generate_embedding(description_text)
            
            # Vérifie si le produit existe déjà
            existing = self.collection.get(ids=[product_id])
            if existing['ids']:
                # Met à jour l'embedding existant
                self.collection.update(
                    ids=[product_id],
                    embeddings=[vector_data],
                    documents=[description_text],
                    metadatas=[{"product_id": product_id, "type": "product"}]
                )
            else:
                # Ajoute un nouvel embedding
                self.collection.add(
                    ids=[product_id],
                    embeddings=[vector_data],
                    documents=[description_text],
                    metadatas=[{"product_id": product_id, "type": "product"}]
                )
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'ajout de l'embedding: {e}")
            return False
    
    def search_similar_products(self, query_text: str, top_k: int = 3) -> List[Dict]:
        """
        Recherche des produits similaires basée sur une requête textuelle
        
        Args:
            query_text: Texte de la requête
            top_k: Nombre maximum de résultats à retourner
        
        Returns:
            List[Dict]: Liste des produits similaires avec leurs scores
        """
        try:
            # Génère l'embedding de la requête
            query_embedding = self.generate_embedding(query_text)
            
            # Recherche dans la base vectorielle
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['metadatas', 'documents', 'distances']
            )
            
            # Formate les résultats
            similar_products = []
            if results['ids'] and results['ids'][0]:
                for i, product_id in enumerate(results['ids'][0]):
                    similar_products.append({
                        'product_id': product_id,
                        'description': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': 1.0 - results['distances'][0][i]  # Convertit distance en similarité
                    })
            
            return similar_products
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
    
    def search_by_product_name(self, product_name: str, top_k: int = 3) -> List[Dict]:
        """
        Recherche des produits similaires basée sur le nom d'un produit existant
        
        Args:
            product_name: Nom du produit de référence
            top_k: Nombre maximum de résultats à retourner
        
        Returns:
            List[Dict]: Liste des produits similaires
        """
        # Crée une description basée sur le nom du produit
        query_text = f"produit similaire à {product_name}"
        return self.search_similar_products(query_text, top_k)
    
    def get_product_embedding(self, product_id: str) -> Optional[List[float]]:
        """
        Récupère l'embedding d'un produit spécifique
        
        Args:
            product_id: Identifiant du produit
        
        Returns:
            Optional[List[float]]: Vecteur d'embedding ou None si non trouvé
        """
        try:
            results = self.collection.get(ids=[product_id])
            if results['embeddings']:
                return results['embeddings'][0]
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération de l'embedding: {e}")
            return None
    
    def update_product_embedding(self, product_id: str, new_description: str) -> bool:
        """
        Met à jour l'embedding d'un produit avec une nouvelle description
        
        Args:
            product_id: Identifiant du produit
            new_description: Nouvelle description du produit
        
        Returns:
            bool: True si la mise à jour a réussi
        """
        new_embedding = self.generate_embedding(new_description)
        return self.add_product_embedding(product_id, new_description, new_embedding)
    
    def delete_product_embedding(self, product_id: str) -> bool:
        """
        Supprime l'embedding d'un produit
        
        Args:
            product_id: Identifiant du produit à supprimer
        
        Returns:
            bool: True si la suppression a réussi
        """
        try:
            self.collection.delete(ids=[product_id])
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression: {e}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """
        Récupère les statistiques de la collection
        
        Returns:
            Dict: Statistiques de la collection
        """
        try:
            count = self.collection.count()
            return {
                "total_products": count,
                "collection_name": self.collection.name,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des stats: {e}")
            return {"error": str(e)}
    
    def clear_collection(self) -> bool:
        """
        Vide complètement la collection
        
        Returns:
            bool: True si le vidage a réussi
        """
        try:
            self.collection.delete(where={})
            return True
        except Exception as e:
            print(f"Erreur lors du vidage: {e}")
            return False 