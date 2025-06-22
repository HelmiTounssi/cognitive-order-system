"""
Module RAG Chat Interface - Interface de chat conversationnel RAG
Interface utilisateur pour interagir avec le système RAG
"""

import json
import logging
import re
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from src.rag.rag_system import HybridRAGSystem, RAGResponse

@dataclass
class ChatMessage:
    """Message de chat"""
    id: str
    content: str
    sender: str  # 'user' ou 'assistant'
    timestamp: datetime
    metadata: Dict
    rag_context: Optional[Dict] = None

@dataclass
class Conversation:
    """Conversation complète"""
    id: str
    title: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    domain: str
    summary: Dict

class RAGChatInterface:
    """
    Interface de chat RAG avec gestion des conversations
    """
    
    def __init__(self, rag_system: HybridRAGSystem):
        self.rag_system = rag_system
        self.conversations: Dict[str, Conversation] = {}
        self.active_conversation_id: Optional[str] = None
    
    def start_new_conversation(self, initial_query: str = None) -> str:
        """Démarre une nouvelle conversation"""
        conversation_id = str(uuid.uuid4())
        
        # Créer la conversation
        conversation = Conversation(
            id=conversation_id,
            title=initial_query[:50] + "..." if initial_query else "Nouvelle conversation",
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            domain='generic',
            summary={}
        )
        
        self.conversations[conversation_id] = conversation
        self.active_conversation_id = conversation_id
        
        # Si une requête initiale est fournie, la traiter
        if initial_query:
            self.send_message(initial_query, conversation_id)
        
        return conversation_id
    
    def send_message(self, message: str, conversation_id: str = None) -> ChatMessage:
        """Envoie un message et génère une réponse RAG"""
        if not conversation_id:
            conversation_id = self.active_conversation_id
        
        if not conversation_id or conversation_id not in self.conversations:
            conversation_id = self.start_new_conversation()
        
        conversation = self.conversations[conversation_id]
        
        # Créer le message utilisateur
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            content=message,
            sender='user',
            timestamp=datetime.now(),
            metadata={}
        )
        
        conversation.messages.append(user_message)
        conversation.updated_at = datetime.now()
        
        # Générer la réponse RAG
        rag_response = self.rag_system.generate_rag_response(message, conversation_id)
        
        # Créer le message assistant
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            content=rag_response.answer,
            sender='assistant',
            timestamp=datetime.now(),
            metadata={
                'confidence': rag_response.confidence,
                'sources_count': len(rag_response.sources),
                'suggested_actions': rag_response.suggested_actions
            },
            rag_context=asdict(rag_response)
        )
        
        conversation.messages.append(assistant_message)
        conversation.updated_at = datetime.now()
        
        # Mettre à jour le domaine et le résumé
        self._update_conversation_metadata(conversation)
        
        return assistant_message
    
    def _update_conversation_metadata(self, conversation: Conversation):
        """Met à jour les métadonnées de la conversation"""
        # Détecter le domaine
        all_text = ' '.join([msg.content for msg in conversation.messages])
        conversation.domain = self._detect_domain(all_text)
        
        # Mettre à jour le titre si nécessaire
        if len(conversation.messages) == 2:  # Premier échange
            first_query = conversation.messages[0].content
            conversation.title = first_query[:50] + "..." if len(first_query) > 50 else first_query
        
        # Générer le résumé
        conversation.summary = self._generate_conversation_summary(conversation)
    
    def _detect_domain(self, text: str) -> str:
        """Détecte le domaine à partir du texte"""
        text_lower = text.lower()
        
        domain_keywords = {
            'healthcare': ['médical', 'patient', 'diagnostic', 'traitement', 'santé', 'médecin'],
            'ecommerce': ['commande', 'produit', 'client', 'paiement', 'livraison', 'achat'],
            'restaurant': ['menu', 'réservation', 'table', 'cuisine', 'restaurant', 'plat']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return domain
        
        return 'generic'
    
    def _generate_conversation_summary(self, conversation: Conversation) -> Dict:
        """Génère un résumé de la conversation"""
        return {
            'total_messages': len(conversation.messages),
            'user_messages': len([m for m in conversation.messages if m.sender == 'user']),
            'assistant_messages': len([m for m in conversation.messages if m.sender == 'assistant']),
            'average_confidence': self._calculate_average_confidence(conversation),
            'topics_discussed': self._extract_topics(conversation),
            'suggested_actions_count': self._count_suggested_actions(conversation)
        }
    
    def _calculate_average_confidence(self, conversation: Conversation) -> float:
        """Calcule la confiance moyenne des réponses"""
        confidences = [
            msg.metadata.get('confidence', 0) 
            for msg in conversation.messages 
            if msg.sender == 'assistant'
        ]
        return sum(confidences) / len(confidences) if confidences else 0
    
    def _extract_topics(self, conversation: Conversation) -> List[str]:
        """Extrait les sujets principaux de la conversation"""
        # Implémentation simple - peut être améliorée avec NLP
        topics = set()
        for message in conversation.messages:
            content = message.content.lower()
            if 'workflow' in content:
                topics.add('workflows')
            if 'règle' in content or 'rule' in content:
                topics.add('règles métier')
            if 'pattern' in content:
                topics.add('patterns d\'extraction')
            if 'commande' in content:
                topics.add('commandes')
            if 'client' in content:
                topics.add('clients')
        
        return list(topics)
    
    def _count_suggested_actions(self, conversation: Conversation) -> int:
        """Compte le nombre total d'actions suggérées"""
        count = 0
        for message in conversation.messages:
            if message.sender == 'assistant':
                actions = message.metadata.get('suggested_actions', [])
                count += len(actions)
        return count
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Récupère une conversation par son ID"""
        return self.conversations.get(conversation_id)
    
    def get_all_conversations(self) -> List[Dict]:
        """Récupère toutes les conversations sous forme de liste"""
        conversations = []
        for conv in self.conversations.values():
            conversations.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'domain': conv.domain,
                'message_count': len(conv.messages),
                'summary': conv.summary
            })
        
        # Trier par date de mise à jour (plus récent en premier)
        conversations.sort(key=lambda x: x['updated_at'], reverse=True)
        return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Supprime une conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            
            # Si c'était la conversation active, la réinitialiser
            if self.active_conversation_id == conversation_id:
                self.active_conversation_id = None
            
            return True
        return False
    
    def export_conversation(self, conversation_id: str) -> Dict:
        """Exporte une conversation au format JSON"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        return {
            'conversation_id': conversation.id,
            'title': conversation.title,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'domain': conversation.domain,
            'summary': conversation.summary,
            'messages': [
                {
                    'id': msg.id,
                    'content': msg.content,
                    'sender': msg.sender,
                    'timestamp': msg.timestamp.isoformat(),
                    'metadata': msg.metadata,
                    'rag_context': msg.rag_context
                }
                for msg in conversation.messages
            ]
        }
    
    def import_conversation(self, conversation_data: Dict) -> str:
        """Importe une conversation depuis un fichier JSON"""
        try:
            conversation_id = conversation_data.get('conversation_id', str(uuid.uuid4()))
            
            # Créer la conversation
            conversation = Conversation(
                id=conversation_id,
                title=conversation_data.get('title', 'Conversation importée'),
                messages=[],
                created_at=datetime.fromisoformat(conversation_data.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(conversation_data.get('updated_at', datetime.now().isoformat())),
                domain=conversation_data.get('domain', 'generic'),
                summary=conversation_data.get('summary', {})
            )
            
            # Importer les messages
            for msg_data in conversation_data.get('messages', []):
                message = ChatMessage(
                    id=msg_data.get('id', str(uuid.uuid4())),
                    content=msg_data.get('content', ''),
                    sender=msg_data.get('sender', 'user'),
                    timestamp=datetime.fromisoformat(msg_data.get('timestamp', datetime.now().isoformat())),
                    metadata=msg_data.get('metadata', {}),
                    rag_context=msg_data.get('rag_context')
                )
                conversation.messages.append(message)
            
            self.conversations[conversation_id] = conversation
            return conversation_id
            
        except Exception as e:
            print(f"Erreur lors de l'import de conversation: {e}")
            return None
    
    def get_suggestions(self, conversation_id: str = None) -> List[str]:
        """Génère des suggestions de questions basées sur le contexte"""
        if not conversation_id:
            conversation_id = self.active_conversation_id
        
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        suggestions = []
        domain = conversation.domain
        
        # Suggestions basées sur le domaine
        domain_suggestions = {
            'healthcare': [
                "Comment créer un workflow de diagnostic médical ?",
                "Quels patterns d'extraction pour les symptômes ?",
                "Comment gérer les règles de contre-indication ?"
            ],
            'ecommerce': [
                "Comment optimiser le processus de commande ?",
                "Quels patterns pour extraire les informations client ?",
                "Comment gérer les règles de validation de paiement ?"
            ],
            'restaurant': [
                "Comment gérer les réservations de table ?",
                "Quels patterns pour les menus et prix ?",
                "Comment optimiser le service client ?"
            ],
            'generic': [
                "Comment créer un nouveau workflow ?",
                "Quels sont les patterns d'extraction disponibles ?",
                "Comment configurer des règles métier ?"
            ]
        }
        
        suggestions.extend(domain_suggestions.get(domain, domain_suggestions['generic']))
        
        # Suggestions basées sur l'historique
        if conversation.messages:
            last_message = conversation.messages[-1]
            if last_message.sender == 'assistant':
                # Si la dernière réponse était de l'assistant, suggérer des questions de suivi
                suggestions.extend([
                    "Pouvez-vous expliquer plus en détail ?",
                    "Comment appliquer cette solution ?",
                    "Y a-t-il d'autres alternatives ?"
                ])
        
        return suggestions[:5]  # Limiter à 5 suggestions
    
    def get_conversation_analytics(self, conversation_id: str = None) -> Dict:
        """Récupère des analytics détaillés pour une conversation"""
        if not conversation_id:
            conversation_id = self.active_conversation_id
        
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return {}
        
        # Calculer les métriques
        total_messages = len(conversation.messages)
        user_messages = len([m for m in conversation.messages if m.sender == 'user'])
        assistant_messages = len([m for m in conversation.messages if m.sender == 'assistant'])
        
        # Confiance moyenne
        confidences = [
            msg.metadata.get('confidence', 0) 
            for msg in conversation.messages 
            if msg.sender == 'assistant'
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Sources utilisées
        sources_used = set()
        for msg in conversation.messages:
            if msg.rag_context and msg.rag_context.get('sources'):
                for source in msg.rag_context['sources']:
                    sources_used.add(source.get('type', 'unknown'))
        
        return {
            'conversation_id': conversation_id,
            'total_messages': total_messages,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'average_confidence': avg_confidence,
            'sources_used': list(sources_used),
            'domain': conversation.domain,
            'duration_minutes': self._calculate_duration(conversation),
            'topics': self._extract_topics(conversation),
            'suggested_actions_count': self._count_suggested_actions(conversation)
        }
    
    def _calculate_duration(self, conversation: Conversation) -> float:
        """Calcule la durée de la conversation en minutes"""
        if len(conversation.messages) < 2:
            return 0
        
        start_time = conversation.messages[0].timestamp
        end_time = conversation.messages[-1].timestamp
        duration = end_time - start_time
        return duration.total_seconds() / 60 