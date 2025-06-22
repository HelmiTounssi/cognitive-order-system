# 🧠 Système de Gestion Cognitif de Commande

Un système intelligent de gestion de commandes utilisant l'inférence sémantique, la recherche vectorielle et le protocole MCP (Model Context Protocol).

## 🚀 Fonctionnalités

### Core Features
- **Base de Connaissances Sémantique** : Ontologie RDF pour la gestion des entités métier
- **Recherche Vectorielle** : Embeddings et similarité sémantique pour les produits
- **Moteur de Règles Avancé** : Règles métier dynamiques et workflow automation
- **Interface LLM** : Intégration avec OpenAI pour le traitement en langage naturel
- **Système RAG** : Retrieval-Augmented Generation pour des réponses contextuelles

### MCP (Model Context Protocol)
- **Serveur MCP** : Exposition des outils via WebSocket
- **Client MCP** : Communication avec les agents externes
- **Interface Admin** : Gestion des outils MCP via interface web

### Architecture Modulaire
```
src/
├── core/           # Composants principaux (agent, knowledge base, rule engine)
├── rag/            # Système RAG et vector store
├── llm/            # Interfaces LLM et assistants
├── mcp/            # Protocole MCP (serveur, client, outils)
├── api/            # API REST et endpoints
├── config/         # Gestionnaire de configuration
├── plugins/        # Système de plugins
└── utils/          # Utilitaires
```

## 📋 Prérequis

- Python 3.8+
- OpenAI API Key (pour les fonctionnalités LLM)
- Git

## 🛠️ Installation

### 1. Cloner le repository
```bash
git clone <votre-repo-url>
cd poc2
```

### 2. Créer un environnement virtuel
```bash
python -m venv poc_env
```

### 3. Activer l'environnement virtuel
**Windows:**
```powershell
poc_env\Scripts\activate
```

**Linux/Mac:**
```bash
source poc_env/bin/activate
```

### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 5. Configuration
Créer un fichier `.env` à la racine du projet :
```env
OPENAI_API_KEY=votre_clé_api_openai
```

## 🚀 Démarrage Rapide

### 1. Démarrer le serveur MCP
```bash
python start_mcp_server.py
```

### 2. Démarrer l'interface admin
```bash
python start_admin_api.py
```

### 3. Démarrer le frontend
```bash
python start_frontend.py
```

### 4. Accéder à l'interface
- **Admin Interface** : http://localhost:5000
- **MCP Server** : ws://localhost:8002

## 📖 Utilisation

### Interface Admin
L'interface admin permet de :
- Gérer les règles métier
- Configurer l'ontologie
- Tester les outils MCP
- Monitorer le système

### API REST
```bash
# Lister les règles
curl http://localhost:5000/api/rules

# Créer une règle
curl -X POST http://localhost:5000/api/rules \
  -H "Content-Type: application/json" \
  -d '{"name": "Nouvelle Règle", "description": "...", ...}'
```

### MCP Tools
Le serveur MCP expose les outils suivants :
- `create_order` : Créer une commande
- `check_stock` : Vérifier le stock
- `process_payment` : Traiter un paiement
- `recommend_products` : Recommander des produits
- Et bien d'autres...

## 🧪 Tests

```bash
# Tests unitaires
python -m pytest tests/

# Tests d'intégration MCP
python test_mcp_integration.py

# Tests complets du système
python test_system_complete.py
```

## 📁 Structure du Projet

```
poc2/
├── src/                    # Code source principal
│   ├── core/              # Composants principaux
│   ├── rag/               # Système RAG
│   ├── llm/               # Interfaces LLM
│   ├── mcp/               # Protocole MCP
│   ├── api/               # API REST
│   ├── config/            # Configuration
│   ├── plugins/           # Plugins
│   └── utils/             # Utilitaires
├── admin-frontend/        # Interface React
├── tests/                 # Tests unitaires
├── scripts/               # Scripts utilitaires
├── configs/               # Fichiers de configuration
├── examples/              # Exemples d'utilisation
└── docs/                  # Documentation
```

## 🔧 Configuration

### Variables d'environnement
- `OPENAI_API_KEY` : Clé API OpenAI
- `MCP_SERVER_PORT` : Port du serveur MCP (défaut: 8002)
- `ADMIN_API_PORT` : Port de l'API admin (défaut: 5000)

### Fichiers de configuration
Les configurations sont stockées dans `configs/` :
- `business_config_*.json` : Configurations métier
- `ontology_*.yaml` : Définitions d'ontologie

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
1. Consulter la documentation dans `docs/`
2. Vérifier les issues existantes
3. Créer une nouvelle issue avec les détails du problème

## 🗺️ Roadmap

- [ ] Support multi-langues
- [ ] Interface graphique avancée
- [ ] Intégration avec d'autres LLM
- [ ] Système de plugins étendu
- [ ] Monitoring et analytics
- [ ] Déploiement Docker

---

**Développé avec ❤️ pour la recherche en IA cognitive** 