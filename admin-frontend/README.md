# 🧠 Interface d'Administration - Système Cognitif

Interface web moderne pour l'administration du système de gestion cognitif de commandes.

## 🎯 Structure Ergonomique

L'interface a été restructurée pour une meilleure expérience utilisateur avec **6 onglets principaux** au lieu de 9 :

### 1. 🏠 **Dashboard**
- Vue d'ensemble du système
- Statut des composants en temps réel
- Métriques de performance
- Actions rapides
- Activité récente
- Santé du système

### 2. 🔧 **Configuration**
- Gestionnaire de configuration unifié
- Import/Export de configurations
- Paramètres système
- Variables d'environnement

### 3. 🧠 **IA & RAG**
- **Assistants LLM** : Génération de workflows et patterns
- **Interface RAG Chat** : Chat intelligent avec recherche contextuelle
- Regroupement logique des fonctionnalités IA

### 4. 🛠️ **Outils & MCP**
- **Serveur MCP** : Gestion du protocole Model Context Protocol
- **Outils API** : Tests des outils simulés (stock, paiement, livraison)
- Regroupement fonctionnel des outils

### 5. 📚 **Base de Connaissances**
- Gestionnaire d'ontologie
- Entités et relations
- Requêtes sémantiques
- Structure RDF

### 6. ⚙️ **Moteur de Règles**
- Gestion des règles métier
- Workflows automatisés
- Tests de règles
- Statistiques d'exécution

## 🚀 Démarrage

### Prérequis
```bash
npm install
```

### Développement
```bash
npm run dev
```

### Production
```bash
npm run build
npm run preview
```

## 🎨 Design System

### Couleurs
- **Primary** : Bleu (#1976d2) - Actions principales
- **Secondary** : Violet (#9c27b0) - Actions secondaires
- **Success** : Vert (#2e7d32) - Statuts positifs
- **Warning** : Orange (#ed6c02) - Avertissements
- **Error** : Rouge (#d32f2f) - Erreurs

### Typographie
- **H1-H6** : Roboto pour les titres
- **Body** : Roboto pour le contenu
- **Monospace** : Consolas pour les logs et code

### Composants
- **Cards** : Conteneurs principaux avec ombres subtiles
- **Chips** : Indicateurs de statut colorés
- **Buttons** : Actions avec icônes et couleurs cohérentes
- **Progress** : Barres de progression pour les métriques

## 📱 Responsive Design

L'interface s'adapte automatiquement aux différentes tailles d'écran :

- **Desktop** (>1200px) : Layout complet avec sidebar
- **Tablet** (768px-1200px) : Layout adaptatif
- **Mobile** (<768px) : Layout empilé optimisé

## 🔧 Configuration

### Variables d'environnement
```env
VITE_API_BASE_URL=http://localhost:5001
VITE_MCP_SERVER_URL=ws://localhost:8002
VITE_APP_TITLE=Système Cognitif
```

### Thème personnalisable
Le thème Material-UI peut être modifié dans `src/theme.ts`

## 🧪 Tests

```bash
# Tests unitaires
npm run test

# Tests de composants
npm run test:components

# Couverture de code
npm run test:coverage
```

## 📊 Métriques

L'interface collecte et affiche :
- **Performance** : Temps de réponse, requêtes/min
- **Ressources** : CPU, mémoire, disque
- **Disponibilité** : Uptime des composants
- **Activité** : Logs en temps réel

## 🔌 Intégrations

### API REST
- Endpoints pour la gestion des règles
- Configuration système
- Tests d'outils

### WebSocket MCP
- Communication temps réel
- Gestion des outils MCP
- Statut du serveur

### RAG System
- Chat intelligent
- Recherche contextuelle
- Historique des conversations

## 🚀 Améliorations Futures

- [ ] **Mode sombre** : Thème sombre pour l'interface
- [ ] **Notifications** : Système de notifications push
- [ ] **Graphiques** : Visualisations avancées des métriques
- [ ] **Export** : Export PDF/Excel des rapports
- [ ] **Multi-langues** : Support internationalisation
- [ ] **PWA** : Application web progressive

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Créer une Pull Request

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

---

**Développé avec ❤️ et Material-UI** 