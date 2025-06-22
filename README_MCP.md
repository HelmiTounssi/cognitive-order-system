# Serveur MCP (Model Context Protocol)

Ce document explique comment utiliser le serveur MCP intégré dans le système d'agent cognitif.

## Qu'est-ce que MCP ?

Le **Model Context Protocol (MCP)** est un protocole standardisé qui permet aux agents IA de communiquer avec des serveurs d'outils via des WebSockets. Cela permet une séparation claire entre l'agent et les outils, facilitant la distribution et la scalabilité.

## Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Agent MCP     │ ◄─────────────► │  Serveur MCP    │
│   (Client)      │                 │  (Tools)        │
└─────────────────┘                 └─────────────────┘
```

## Composants

### 1. Serveur MCP (`src/mcp_server.py`)

Le serveur MCP expose tous les outils existants via le protocole MCP :

- **Port par défaut** : 8001
- **Protocole** : WebSocket
- **Outils exposés** : Tous les outils du module `tools.py`

### 2. Client MCP (`src/mcp_client.py`)

Le client MCP permet à l'agent de communiquer avec le serveur :

- **Interface synchrone** : `MCPToolInterface`
- **Interface asynchrone** : `MCPClient`
- **Gestion automatique** : Connexion/déconnexion

### 3. Agent MCP (`src/agent.py`)

L'agent a été modifié pour supporter MCP :

- **Paramètre `use_mcp`** : Active/désactive MCP
- **Fallback automatique** : Utilise les outils locaux si MCP échoue
- **Transparence** : Même interface utilisateur

## Utilisation

### 1. Démarrage du serveur MCP

```bash
# Option 1: Script dédié
python start_mcp_server.py

# Option 2: Directement
python -c "
import asyncio
from src.mcp_server import start_mcp_server
from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore

kb = KnowledgeBase()
vs = VectorStore()
asyncio.run(start_mcp_server(kb, vs))
"
```

### 2. Utilisation de l'agent avec MCP

```python
from src.agent import CognitiveOrderAgent
from src.knowledge_base import KnowledgeBase
from src.vector_store import VectorStore

# Initialisation
kb = KnowledgeBase()
vs = VectorStore()

# Agent avec MCP activé
agent = CognitiveOrderAgent(
    knowledge_base=kb,
    vector_store=vs,
    use_mcp=True,  # Active MCP
    mcp_server_url="ws://localhost:8001"
)

# Utilisation normale
response = agent.run_agent("lister les clients")
print(response)
```

### 3. Appels directs aux outils MCP

```python
# Liste les outils disponibles
tools_list = agent.list_available_tools_via_mcp()
print(tools_list)

# Appel direct d'un outil
result = agent.call_tool_via_mcp("list_clients", {})
print(result)
```

## Outils disponibles via MCP

Le serveur MCP expose les outils suivants :

### Gestion des commandes
- `create_order` - Créer une commande
- `validate_order` - Valider une commande
- `process_payment` - Traiter un paiement
- `get_all_orders` - Lister toutes les commandes

### Gestion des clients
- `add_client` - Ajouter un client
- `list_clients` - Lister les clients
- `get_client_details` - Détails d'un client

### Gestion des produits
- `check_stock` - Vérifier le stock
- `get_product_details` - Détails d'un produit
- `recommend_products` - Recommander des produits

### Ontologie
- `introspect_ontology` - Analyser l'ontologie
- `extend_ontology` - Étendre l'ontologie
- `create_instance` - Créer une instance
- `query_ontology` - Requêter l'ontologie

### Comportements et réflexion
- `add_behavior_class` - Ajouter une classe de comportement
- `add_state_machine` - Ajouter une machine à états
- `execute_behavior` - Exécuter un comportement
- `create_semantic_proxy` - Créer un proxy sémantique
- `execute_method_reflection` - Exécuter une méthode via réflexion
- `reflect_class` - Analyser une classe
- `instantiate_by_reflection` - Instancier via réflexion

## Avantages de MCP

### 1. Séparation des responsabilités
- L'agent se concentre sur la logique métier
- Les outils sont isolés dans le serveur MCP

### 2. Scalabilité
- Plusieurs agents peuvent utiliser le même serveur MCP
- Distribution possible sur différents serveurs

### 3. Standardisation
- Protocole standard MCP
- Compatible avec d'autres implémentations MCP

### 4. Flexibilité
- Fallback automatique vers les outils locaux
- Activation/désactivation à la volée

## Tests

### Test d'intégration

```bash
python test_mcp_integration.py
```

Ce script teste :
- Démarrage du serveur MCP
- Connexion de l'agent
- Appels d'outils
- Comparaison MCP vs local

### Test manuel

```python
# Test simple
from test_mcp_integration import test_mcp_integration
test_mcp_integration()
```

## Configuration

### Variables d'environnement

```bash
# URL du serveur MCP (optionnel)
export MCP_SERVER_URL="ws://localhost:8001"

# Port du serveur MCP (optionnel)
export MCP_SERVER_PORT="8001"
```

### Configuration dans le code

```python
# Dans l'agent
agent = CognitiveOrderAgent(
    knowledge_base=kb,
    vector_store=vs,
    use_mcp=True,
    mcp_server_url="ws://your-server:8001"
)

# Dans le serveur
await start_mcp_server(kb, vs, host="0.0.0.0", port=8001)
```

## Dépannage

### Erreur de connexion

```
❌ Erreur de connexion au serveur MCP: Connection refused
```

**Solution** : Vérifiez que le serveur MCP est démarré sur le bon port.

### Outils non disponibles

```
❌ Serveur MCP non disponible
```

**Solution** : Vérifiez la connexion et les permissions.

### Performance lente

**Solution** : Utilisez les outils locaux pour les opérations critiques.

## Développement

### Ajouter un nouvel outil

1. Ajoutez l'outil dans `src/tools.py`
2. Enregistrez-le dans `src/mcp_server.py` (méthode `_register_tools`)
3. Testez via MCP

### Modifier le protocole

Le serveur MCP suit le protocole MCP standard. Consultez la [documentation officielle](https://modelcontextprotocol.io/) pour plus de détails.

## Sécurité

- Le serveur MCP écoute uniquement sur localhost par défaut
- Utilisez HTTPS/WSS en production
- Implémentez l'authentification si nécessaire

## Support

Pour toute question ou problème avec MCP :

1. Vérifiez les logs du serveur MCP
2. Testez la connexion WebSocket
3. Consultez la documentation MCP officielle 