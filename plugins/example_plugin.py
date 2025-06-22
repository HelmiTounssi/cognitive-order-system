#!/usr/bin/env python3
"""
Plugin d'exemple - Démonstration du système de plugins
Ce plugin montre comment créer des plugins pour étendre le système cognitif
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Ajouter la racine du projet au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.plugin_manager import PluginManager
from src.knowledge_base import KnowledgeBase


class ExamplePlugin:
    """
    Plugin d'exemple démontrant les capacités d'extension du système
    """
    
    def __init__(self):
        self.name = "example_plugin"
        self.version = "1.0.0"
        self.description = "Plugin d'exemple pour démontrer les fonctionnalités"
        self.author = "Système Cognitif"
        self.category = "demo"
        
        # Métadonnées du plugin
        self.metadata = {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'category': self.category,
            'created_at': datetime.now().isoformat(),
            'dependencies': [],
            'tags': ['demo', 'example', 'tutorial']
        }
        
        # Fonctions exposées par le plugin
        self.functions = {
            'hello_world': self.hello_world,
            'process_data': self.process_data,
            'analyze_text': self.analyze_text,
            'generate_report': self.generate_report,
            'custom_business_logic': self.custom_business_logic
        }
        
        # Configuration du plugin
        self.config = {
            'enabled': True,
            'auto_load': True,
            'settings': {
                'max_items': 100,
                'timeout': 30,
                'debug_mode': False
            }
        }
    
    def hello_world(self, name: str = "Monde") -> str:
        """
        Fonction simple de démonstration
        
        Args:
            name: Nom à saluer
            
        Returns:
            Message de salutation
        """
        return f"👋 Bonjour {name} ! Ceci est un plugin d'exemple."
    
    def process_data(self, data: List[Dict]) -> Dict:
        """
        Traite des données et applique une logique métier personnalisée
        
        Args:
            data: Liste de données à traiter
            
        Returns:
            Résultat du traitement
        """
        if not data:
            return {'error': 'Aucune donnée fournie'}
        
        # Logique de traitement personnalisée
        processed_items = []
        total_value = 0
        
        for item in data:
            # Exemple de traitement : calculer une valeur
            value = item.get('value', 0)
            processed_item = {
                'id': item.get('id', 'unknown'),
                'original_value': value,
                'processed_value': value * 1.1,  # +10%
                'timestamp': datetime.now().isoformat()
            }
            processed_items.append(processed_item)
            total_value += processed_item['processed_value']
        
        return {
            'processed_items': processed_items,
            'total_value': total_value,
            'item_count': len(processed_items),
            'processing_time': datetime.now().isoformat()
        }
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyse un texte et extrait des informations
        
        Args:
            text: Texte à analyser
            
        Returns:
            Résultats de l'analyse
        """
        if not text:
            return {'error': 'Aucun texte fourni'}
        
        # Analyse simple du texte
        words = text.split()
        sentences = text.split('.')
        
        analysis = {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'character_count': len(text),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'contains_numbers': any(char.isdigit() for char in text),
            'contains_uppercase': any(char.isupper() for char in text),
            'language_detection': 'french' if any(word in ['le', 'la', 'les', 'de', 'et', 'ou'] for word in words) else 'unknown'
        }
        
        return analysis
    
    def generate_report(self, data: Dict, report_type: str = "summary") -> str:
        """
        Génère un rapport basé sur les données fournies
        
        Args:
            data: Données pour le rapport
            report_type: Type de rapport à générer
            
        Returns:
            Rapport généré
        """
        if report_type == "summary":
            return self._generate_summary_report(data)
        elif report_type == "detailed":
            return self._generate_detailed_report(data)
        else:
            return f"Type de rapport '{report_type}' non supporté"
    
    def _generate_summary_report(self, data: Dict) -> str:
        """Génère un rapport de synthèse"""
        report = f"""
📊 RAPPORT DE SYNTHÈSE
{'=' * 40}

📅 Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📋 Données analysées: {len(data) if isinstance(data, dict) else 'N/A'}

🔍 Points clés:
"""
        
        if isinstance(data, dict):
            for key, value in data.items():
                report += f"   • {key}: {value}\n"
        
        report += f"""
✅ Rapport généré par le plugin d'exemple
"""
        return report
    
    def _generate_detailed_report(self, data: Dict) -> str:
        """Génère un rapport détaillé"""
        report = f"""
📋 RAPPORT DÉTAILLÉ
{'=' * 50}

📅 Date de génération: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 Plugin: {self.name} v{self.version}
👤 Auteur: {self.author}

📊 ANALYSE DÉTAILLÉE:
"""
        
        if isinstance(data, dict):
            for key, value in data.items():
                report += f"\n🔹 {key.upper()}:\n"
                if isinstance(value, (list, dict)):
                    report += f"   {json.dumps(value, indent=2, ensure_ascii=False)}\n"
                else:
                    report += f"   {value}\n"
        
        report += f"""
📈 MÉTRIQUES:
   • Nombre d'éléments: {len(data) if isinstance(data, dict) else 0}
   • Taille des données: {len(str(data))} caractères
   • Type de données: {type(data).__name__}

✅ Rapport détaillé généré avec succès
"""
        return report
    
    def custom_business_logic(self, business_data: Dict) -> Dict:
        """
        Logique métier personnalisée pour le domaine d'activité
        
        Args:
            business_data: Données métier à traiter
            
        Returns:
            Résultat de la logique métier
        """
        # Exemple de logique métier : calcul de remise
        total_amount = business_data.get('amount', 0)
        customer_type = business_data.get('customer_type', 'standard')
        
        # Calcul de remise selon le type de client
        discount_rates = {
            'vip': 0.15,      # 15% de remise
            'premium': 0.10,  # 10% de remise
            'standard': 0.05, # 5% de remise
            'new': 0.02       # 2% de remise
        }
        
        discount_rate = discount_rates.get(customer_type, 0.0)
        discount_amount = total_amount * discount_rate
        final_amount = total_amount - discount_amount
        
        return {
            'original_amount': total_amount,
            'customer_type': customer_type,
            'discount_rate': discount_rate,
            'discount_amount': discount_amount,
            'final_amount': final_amount,
            'savings_percentage': (discount_amount / total_amount * 100) if total_amount > 0 else 0,
            'calculation_date': datetime.now().isoformat()
        }
    
    def get_info(self) -> Dict:
        """Retourne les informations du plugin"""
        return {
            'metadata': self.metadata,
            'config': self.config,
            'functions': list(self.functions.keys()),
            'status': 'active' if self.config['enabled'] else 'disabled'
        }
    
    def update_config(self, new_config: Dict) -> bool:
        """Met à jour la configuration du plugin"""
        try:
            self.config.update(new_config)
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la config: {e}")
            return False


def create_plugin() -> ExamplePlugin:
    """Fonction de création du plugin (requise par le système)"""
    return ExamplePlugin()


# Test du plugin
if __name__ == "__main__":
    print("🧪 Test du Plugin d'Exemple")
    print("=" * 40)
    
    # Créer le plugin
    plugin = ExamplePlugin()
    
    # Test des fonctions
    print("\n1. Test hello_world:")
    print(plugin.hello_world("Développeur"))
    
    print("\n2. Test process_data:")
    test_data = [
        {'id': 'item1', 'value': 100},
        {'id': 'item2', 'value': 200},
        {'id': 'item3', 'value': 150}
    ]
    result = plugin.process_data(test_data)
    print(f"Résultat: {result}")
    
    print("\n3. Test analyze_text:")
    text = "Ceci est un exemple de texte en français. Il contient plusieurs phrases."
    analysis = plugin.analyze_text(text)
    print(f"Analyse: {analysis}")
    
    print("\n4. Test custom_business_logic:")
    business_data = {
        'amount': 1000,
        'customer_type': 'vip'
    }
    business_result = plugin.custom_business_logic(business_data)
    print(f"Logique métier: {business_result}")
    
    print("\n5. Test generate_report:")
    report = plugin.generate_report({'test': 'data', 'count': 42})
    print(report)
    
    print("\n✅ Tous les tests du plugin sont réussis !") 