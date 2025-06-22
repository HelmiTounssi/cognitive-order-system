# 🧠 Système Cognitif de Gestion de Commande - Guide de Démarrage

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- Node.js 16+
- Environnement virtuel Python activé

### 1. Activation de l'environnement virtuel
```bash
poc_env\Scripts\activate
```

### 2. Démarrage du système complet
```bash
python start_system.py
```

Le système démarre automatiquement :
- **API Backend** : http://localhost:5000
- **Interface Admin** : http://localhost:5173

### 3. Démarrage séparé (optionnel)

#### Backend uniquement
```bash
python start_admin_api.py
```

#### Frontend uniquement
```bash
python start_frontend.py
```

## 📋 Fonctionnalités Disponibles

### Interface d'Administration (http://localhost:5173)
- **Configuration** : Gestion des configurations YAML/JSON
- **Règles Métier** : Création et gestion des règles
- **Ontologie** : Gestion des entités et classes
- **Assistants LLM** : Génération de workflows et patterns
- **RAG Chat** : Interface de chat conversationnel
- **Statut Système** : Monitoring des composants

### API Backend (http://localhost:5000)
- **/api/rules** - Gestion des règles métier
- **/api/configurations** - Import/Export de configurations
- **/api/ontology** - Gestion de l'ontologie
- **/api/llm** - Assistants LLM
- **/api/rag** - Interface RAG
- **/api/system/status** - Statut du système
- **/api/health** - Vérification de santé

## 🔧 Tests et Validation

### Test du système de plugins
```bash
python scripts/test_plugin_example.py
```

### Test de l'API
```bash
python -c "import requests; print(requests.get('http://localhost:5000/api/health').json())"
```

### Test des configurations
```bash
python scripts/test_yaml_import.py
```

## 📁 Structure du Projet

```
poc2/
├── src/                    # Code source Python
│   ├── api/               # API Flask
│   ├── knowledge_base.py  # Base de connaissances
│   ├── rule_engine.py     # Moteur de règles
│   ├── llm_assistants.py  # Assistants LLM
│   └── ...
├── admin-frontend/        # Interface React
├── plugins/              # Système de plugins
├── scripts/              # Scripts de test
├── examples/             # Exemples de configurations
├── start_system.py       # Script de démarrage principal
├── start_admin_api.py    # Script backend
└── start_frontend.py     # Script frontend
```

## 🎯 Utilisation

### 1. Import de configurations
- Utilisez les fichiers YAML dans `examples/`
- Importez via l'interface ou l'API
- Testez avec `scripts/test_yaml_import.py`

### 2. Gestion des règles
- Créez des règles via l'interface
- Testez avec l'endpoint `/api/rules/test`
- Exportez/importez des règles

### 3. Ontologie
- Ajoutez des entités et classes
- Importez des ontologies existantes
- Utilisez la réflexion pour l'extension dynamique

### 4. Assistants LLM
- Générez des workflows automatiquement
- Créez des patterns d'extraction
- Sauvegardez et appliquez les résultats

### 5. RAG Chat
- Interface conversationnelle
- Recherche hybride (vecteur + graphe)
- Gestion des conversations

## 🛠️ Dépannage

### Erreur "No module named 'yaml'"
```bash
pip install pyyaml
```

### Erreur "No module named 'flask'"
```bash
pip install flask flask-cors
```

### Erreur Node.js
- Installez Node.js depuis https://nodejs.org/
- Vérifiez avec `node --version`

### Ports déjà utilisés
- Backend : Changez le port dans `start_admin_api.py`
- Frontend : Changez le port dans `admin-frontend/vite.config.ts`

## 📚 Documentation

- **Article scientifique** : `article_scientifique_poc.md`
- **Exemples** : Dossier `examples/`
- **Tests** : Dossier `scripts/`
- **Plugins** : Dossier `plugins/`

## 🎉 Système Prêt !

Le système cognitif est maintenant opérationnel avec :
- ✅ Gestion sémantique des connaissances
- ✅ Moteur de règles avancé
- ✅ Interface d'administration complète
- ✅ Système de plugins extensible
- ✅ Assistants LLM intégrés
- ✅ Interface RAG conversationnelle
- ✅ Import/Export de configurations 