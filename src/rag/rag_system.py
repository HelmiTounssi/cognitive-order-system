"""
Module RAG System - Système de Retrieval-Augmented Generation
Implémente une recherche hybride vectorielle + graphe avec génération de réponses
"""

import json
import logging
import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass
from src.core.knowledge_base import KnowledgeBase
from src.rag.vector_store import VectorStore
from src.llm.llm_interface import LLMInterface

logger = logging.getLogger(__name__)

@dataclass
class RAGContext:
    """Contexte pour la génération RAG"""
    query: str
    vector_results: List[Dict]
    graph_results: List[Dict]
    business_context: Dict
    conversation_history: List[Dict]
    timestamp: datetime

@dataclass
class RAGResponse:
    """Réponse RAG structurée"""
    answer: str
    sources: List[Dict]
    confidence: float
    context_used: Dict
    suggested_actions: List[str]
    metadata: Dict

class HybridRAGSystem:
    """
    Système RAG hybride combinant recherche vectorielle et graphique
    """
    
    def __init__(self, knowledge_base: KnowledgeBase, vector_store: VectorStore, llm_interface: LLMInterface):
        self.kb = knowledge_base
        self.vs = vector_store
        self.llm = llm_interface
        self.conversation_history = []
        
        # Configuration RAG
        self.max_context_length = 4000
        self.vector_weight = 0.6
        self.graph_weight = 0.4
        self.min_confidence = 0.3
        
    def search_hybrid(self, query: str, top_k: int = 5) -> Tuple[List[Dict], List[Dict]]:
        """
        Recherche hybride combinant vector et graph
        """
        try:
            # Recherche vectorielle
            vector_results = self.vs.search_similar_products(query, top_k)
            
            # Recherche graphique (sémantique)
            graph_results = self.kb.search_semantic(query, top_k)
            
            # Fusion et scoring hybride
            hybrid_results = self._merge_results(vector_results, graph_results, query)
            
            return vector_results, graph_results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche hybride: {e}")
            return [], []
    
    def _merge_results(self, vector_results: List[Dict], graph_results: List[Dict], query: str) -> List[Dict]:
        """Fusionne et score les résultats vectoriels et graphiques"""
        merged = {}
        
        # Traiter les résultats vectoriels
        for i, result in enumerate(vector_results):
            key = result.get('id', f'vector_{i}')
            merged[key] = {
                'content': result.get('content', ''),
                'score': result.get('score', 0) * self.vector_weight,
                'source': 'vector',
                'metadata': result.get('metadata', {})
            }
        
        # Traiter les résultats graphiques
        for i, result in enumerate(graph_results):
            key = result.get('id', f'graph_{i}')
            if key in merged:
                # Fusionner avec le résultat vectoriel existant
                merged[key]['score'] += result.get('score', 0) * self.graph_weight
                merged[key]['source'] = 'hybrid'
                merged[key]['graph_data'] = result
            else:
                merged[key] = {
                    'content': result.get('content', ''),
                    'score': result.get('score', 0) * self.graph_weight,
                    'source': 'graph',
                    'metadata': result.get('metadata', {}),
                    'graph_data': result
                }
        
        # Trier par score et retourner les meilleurs
        sorted_results = sorted(merged.values(), key=lambda x: x['score'], reverse=True)
        return sorted_results[:10]
    
    def get_business_context(self, query: str) -> Dict:
        """Récupère le contexte métier pertinent"""
        try:
            context = {
                'domain': 'generic',
                'entities': [],
                'rules': [],
                'workflows': [],
                'patterns': []
            }
            
            # Détecter le domaine
            domain_keywords = {
                'healthcare': ['médical', 'patient', 'diagnostic', 'traitement', 'santé'],
                'ecommerce': ['commande', 'produit', 'client', 'paiement', 'livraison'],
                'restaurant': ['menu', 'réservation', 'table', 'cuisine', 'service']
            }
            
            query_lower = query.lower()
            for domain, keywords in domain_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    context['domain'] = domain
                    break
            
            # Récupérer les entités pertinentes
            entities = self.kb.get_all_entities()
            for entity_name, entity_data in entities.items():
                if entity_data.get('source') == 'llm_assistant':
                    if entity_data.get('type') == 'workflow':
                        context['workflows'].append(entity_data)
                    elif entity_data.get('type') == 'extraction_patterns':
                        context['patterns'].append(entity_data)
                    elif entity_data.get('type') == 'business_rules':
                        context['rules'].append(entity_data)
            
            return context
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du contexte métier: {e}")
            return {'domain': 'generic', 'entities': [], 'rules': [], 'workflows': [], 'patterns': []}
    
    def generate_rag_response(self, query: str, conversation_id: str = None) -> RAGResponse:
        """
        Génère une réponse RAG complète
        """
        try:
            # Recherche hybride
            vector_results, graph_results = self.search_hybrid(query)
            
            # Contexte métier
            business_context = self.get_business_context(query)
            
            # Historique de conversation
            conversation_history = self._get_conversation_history(conversation_id)
            
            # Créer le contexte RAG
            rag_context = RAGContext(
                query=query,
                vector_results=vector_results,
                graph_results=graph_results,
                business_context=business_context,
                conversation_history=conversation_history,
                timestamp=datetime.now()
            )
            
            # Générer la réponse
            response = self._generate_answer(rag_context)
            
            # Sauvegarder dans l'historique
            self._save_conversation(conversation_id, query, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération RAG: {e}")
            return RAGResponse(
                answer="Désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer.",
                sources=[],
                confidence=0.0,
                context_used={},
                suggested_actions=[],
                metadata={'error': str(e)}
            )
    
    def _generate_answer(self, context: RAGContext) -> RAGResponse:
        """Génère la réponse finale avec le contexte RAG"""
        try:
            # Préparer le prompt RAG
            prompt = self._build_rag_prompt(context)
            
            # Générer la réponse avec l'LLM
            llm_response = self.llm.generate_response(prompt)
            
            # Parser la réponse
            answer, confidence, sources, actions = self._parse_llm_response(llm_response)
            
            return RAGResponse(
                answer=answer,
                sources=sources,
                confidence=confidence,
                context_used={
                    'vector_results_count': len(context.vector_results),
                    'graph_results_count': len(context.graph_results),
                    'business_context': context.business_context,
                    'domain': context.business_context.get('domain', 'generic')
                },
                suggested_actions=actions,
                metadata={
                    'generation_time': datetime.now().isoformat(),
                    'context_length': len(prompt)
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse: {e}")
            return RAGResponse(
                answer="Erreur lors de la génération de la réponse.",
                sources=[],
                confidence=0.0,
                context_used={},
                suggested_actions=[],
                metadata={'error': str(e)}
            )
    
    def _build_rag_prompt(self, context: RAGContext) -> str:
        """Construit le prompt RAG avec le contexte"""
        prompt = f"""
Vous êtes un assistant métier intelligent spécialisé dans la gestion cognitive de commandes.
Vous avez accès à une base de connaissances riche et à un historique de conversation.

CONTEXTE MÉTIER:
- Domaine: {context.business_context.get('domain', 'generic')}
- Workflows disponibles: {len(context.business_context.get('workflows', []))}
- Patterns d'extraction: {len(context.business_context.get('patterns', []))}
- Règles métier: {len(context.business_context.get('rules', []))}

RÉSULTATS DE RECHERCHE VECTORIELLE:
{self._format_vector_results(context.vector_results)}

RÉSULTATS DE RECHERCHE GRAPHIQUE:
{self._format_graph_results(context.graph_results)}

HISTORIQUE DE CONVERSATION:
{self._format_conversation_history(context.conversation_history)}

QUESTION ACTUELLE: {context.query}

INSTRUCTIONS:
1. Analysez le contexte métier et les résultats de recherche
2. Fournissez une réponse précise et utile
3. Citez vos sources quand c'est pertinent
4. Suggérez des actions concrètes si approprié
5. Adaptez votre réponse au domaine métier identifié

RÉPONSE (format JSON):
{{
    "answer": "Votre réponse détaillée ici",
    "confidence": 0.85,
    "sources": [
        {{"type": "vector", "content": "extrait pertinent", "score": 0.9}},
        {{"type": "graph", "content": "entité métier", "score": 0.8}}
    ],
    "suggested_actions": [
        "Action 1",
        "Action 2"
    ]
}}
"""
        return prompt
    
    def _format_vector_results(self, results: List[Dict]) -> str:
        """Formate les résultats vectoriels pour le prompt"""
        if not results:
            return "Aucun résultat vectoriel pertinent trouvé."
        
        formatted = []
        for i, result in enumerate(results[:3]):  # Top 3
            formatted.append(f"{i+1}. {result.get('content', '')[:200]}... (score: {result.get('score', 0):.2f})")
        
        return "\n".join(formatted)
    
    def _format_graph_results(self, results: List[Dict]) -> str:
        """Formate les résultats graphiques pour le prompt"""
        if not results:
            return "Aucun résultat graphique pertinent trouvé."
        
        formatted = []
        for i, result in enumerate(results[:3]):  # Top 3
            formatted.append(f"{i+1}. {result.get('content', '')[:200]}... (type: {result.get('type', 'unknown')})")
        
        return "\n".join(formatted)
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Formate l'historique de conversation"""
        if not history:
            return "Aucun historique de conversation."
        
        formatted = []
        for entry in history[-3:]:  # Derniers 3 échanges
            formatted.append(f"Q: {entry.get('query', '')}")
            formatted.append(f"R: {entry.get('answer', '')[:100]}...")
        
        return "\n".join(formatted)
    
    def _parse_llm_response(self, response: str) -> Tuple[str, float, List[Dict], List[str]]:
        """Parse la réponse de l'LLM"""
        try:
            # Essayer de parser le JSON
            if response.strip().startswith('{'):
                data = json.loads(response)
                return (
                    data.get('answer', 'Réponse non structurée'),
                    data.get('confidence', 0.5),
                    data.get('sources', []),
                    data.get('suggested_actions', [])
                )
            else:
                # Réponse en texte libre
                return response, 0.5, [], []
                
        except json.JSONDecodeError:
            # Fallback: traiter comme texte libre
            return response, 0.5, [], []
    
    def _get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Récupère l'historique de conversation"""
        if not conversation_id:
            return []
        
        # Pour l'instant, retourner l'historique global
        return self.conversation_history[-5:]  # Derniers 5 échanges
    
    def _save_conversation(self, conversation_id: str, query: str, response: RAGResponse):
        """Sauvegarde l'échange dans l'historique"""
        entry = {
            'conversation_id': conversation_id,
            'query': query,
            'answer': response.answer,
            'timestamp': datetime.now().isoformat(),
            'confidence': response.confidence
        }
        
        self.conversation_history.append(entry)
        
        # Limiter la taille de l'historique
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def get_conversation_summary(self, conversation_id: str = None) -> Dict:
        """Récupère un résumé de la conversation"""
        history = self._get_conversation_history(conversation_id)
        
        return {
            'total_exchanges': len(history),
            'average_confidence': sum(h.get('confidence', 0) for h in history) / len(history) if history else 0,
            'last_exchange': history[-1] if history else None,
            'domain_detected': self._detect_domain_from_history(history)
        }
    
    def _detect_domain_from_history(self, history: List[Dict]) -> str:
        """Détecte le domaine à partir de l'historique"""
        if not history:
            return 'generic'
        
        # Analyser les requêtes pour détecter le domaine
        all_text = ' '.join([h.get('query', '') + ' ' + h.get('answer', '') for h in history])
        all_text_lower = all_text.lower()
        
        domain_keywords = {
            'healthcare': ['médical', 'patient', 'diagnostic', 'traitement'],
            'ecommerce': ['commande', 'produit', 'client', 'paiement'],
            'restaurant': ['menu', 'réservation', 'table', 'cuisine']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in all_text_lower for keyword in keywords):
                return domain
        
        return 'generic' 