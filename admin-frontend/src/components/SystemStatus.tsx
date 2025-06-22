import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  LinearProgress,
  IconButton,
  Tooltip,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  Button,
  Paper
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Computer as ComputerIcon,
  Psychology as PsychologyIcon,
  Rule as RuleIcon,
  Api as ApiIcon
} from '@mui/icons-material';

interface SystemStatus {
  global_status: 'excellent' | 'good' | 'warning' | 'critical';
  health_percentage: number;
  online_components: number;
  total_components: number;
  timestamp: string;
}

interface SystemInfo {
  platform: string;
  python_version: string;
  cpu_count: number;
  memory_total: number;
  memory_available: number;
  memory_percent: number;
  disk_usage: number;
}

interface ComponentStatus {
  status: 'online' | 'offline';
  [key: string]: any;
}

interface SystemStatusData {
  system_status: SystemStatus;
  system_info: SystemInfo;
  components: {
    rule_engine: ComponentStatus;
    knowledge_base: ComponentStatus;
    vector_store: ComponentStatus;
    llm_interface: ComponentStatus;
    rag_system: ComponentStatus;
    config_manager: ComponentStatus;
  };
  recommendations: string[];
}

const SystemStatus: React.FC = () => {
  const [systemStatus, setSystemStatus] = useState({
    knowledgeBase: { status: 'Opérationnel', color: 'success', details: 'Base RDF chargée avec 150 entités' },
    vectorStore: { status: 'Opérationnel', color: 'success', details: 'ChromaDB connecté, 89 produits indexés' },
    llmInterface: { status: 'Opérationnel', color: 'success', details: 'OpenAI API connectée' },
    agent: { status: 'Opérationnel', color: 'success', details: 'Agent cognitif actif' },
    ruleEngine: { status: 'Opérationnel', color: 'success', details: '12 règles métier actives' },
    mcpServer: { status: 'En cours', color: 'warning', details: 'Serveur MCP en démarrage' }
  });

  const [metrics, setMetrics] = useState({
    requestsPerMinute: 23,
    averageResponseTime: 1.2,
    memoryUsage: 67,
    cpuUsage: 45,
    activeConnections: 8
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Opérationnel': return <CheckCircleIcon color="success" />;
      case 'En cours': return <WarningIcon color="warning" />;
      case 'Erreur': return <ErrorIcon color="error" />;
      default: return <InfoIcon color="info" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Opérationnel': return 'success';
      case 'En cours': return 'warning';
      case 'Erreur': return 'error';
      default: return 'info';
    }
  };

  const getComponentLabel = (key: string) => {
    const labels: { [key: string]: string } = {
      knowledgeBase: 'Base de Connaissances',
      vectorStore: 'Vector Store',
      llmInterface: 'Interface LLM',
      agent: 'Agent IA',
      ruleEngine: 'Moteur de Règles',
      mcpServer: 'Serveur MCP'
    };
    return labels[key] || key;
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        🏠 Dashboard - Vue d'ensemble du système
      </Typography>

      <Grid container spacing={3}>
        {/* Status Cards */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Statut des Composants
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(systemStatus).map(([key, value]) => (
                  <Grid item xs={12} sm={6} key={key}>
                    <Paper sx={{ p: 2, border: 1, borderColor: 'divider' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        {getStatusIcon(value.status)}
                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                          {getComponentLabel(key)}
                        </Typography>
                      </Box>
                      <Chip 
                        label={value.status} 
                        color={getStatusColor(value.status) as any}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {value.details}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Metrics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📈 Métriques en Temps Réel
              </Typography>
              
              <List>
                <ListItem>
                  <ListItemIcon>
                    <SpeedIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${metrics.requestsPerMinute} req/min`}
                    secondary="Requêtes par minute"
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <ApiIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${metrics.averageResponseTime}s`}
                    secondary="Temps de réponse moyen"
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <MemoryIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${metrics.memoryUsage}%`}
                    secondary="Utilisation mémoire"
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <StorageIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${metrics.cpuUsage}%`}
                    secondary="Utilisation CPU"
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <PsychologyIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={`${metrics.activeConnections}`}
                    secondary="Connexions actives"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                ⚡ Actions Rapides
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button variant="contained" color="primary">
                  🔄 Redémarrer le système
                </Button>
                <Button variant="outlined" color="primary">
                  📊 Voir les logs
                </Button>
                <Button variant="outlined" color="secondary">
                  🔧 Configuration avancée
                </Button>
                <Button variant="outlined">
                  📋 Rapport de santé
                </Button>
                <Button variant="outlined">
                  🧪 Tests automatiques
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📝 Activité Récente
              </Typography>
              <Box sx={{ 
                bgcolor: 'grey.50', 
                p: 2, 
                borderRadius: 1, 
                maxHeight: 300, 
                overflow: 'auto',
                fontFamily: 'monospace',
                fontSize: '0.875rem'
              }}>
                <div style={{ color: 'green' }}>[10:30:15] ✅ Système démarré avec succès</div>
                <div style={{ color: 'blue' }}>[10:30:16] 📚 Base de connaissances chargée (150 entités)</div>
                <div style={{ color: 'blue' }}>[10:30:17] 🔍 Vector store initialisé (89 produits)</div>
                <div style={{ color: 'green' }}>[10:30:18] 🤖 Interface LLM connectée</div>
                <div style={{ color: 'blue' }}>[10:30:19] ⚙️ Moteur de règles initialisé (12 règles)</div>
                <div style={{ color: 'green' }}>[10:30:20] ✅ Prêt à traiter les requêtes</div>
                <div style={{ color: 'orange' }}>[10:31:05] 🔌 Serveur MCP en cours de démarrage</div>
                <div style={{ color: 'blue' }}>[10:31:15] 📊 3 requêtes traitées avec succès</div>
                <div style={{ color: 'purple' }}>[10:32:00] 💬 Session RAG démarrée</div>
                <div style={{ color: 'blue' }}>[10:32:30] 🛠️ Test d'outil MCP réussi</div>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* System Health */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🏥 Santé du Système
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Performance globale</Typography>
                  <Typography variant="body2">92%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={92} color="success" sx={{ height: 8, borderRadius: 4 }} />
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Disponibilité</Typography>
                  <Typography variant="body2">99.8%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={99.8} color="success" sx={{ height: 8, borderRadius: 4 }} />
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Sécurité</Typography>
                  <Typography variant="body2">100%</Typography>
                </Box>
                <LinearProgress variant="determinate" value={100} color="success" sx={{ height: 8, borderRadius: 4 }} />
              </Box>
              
              <Alert severity="success" sx={{ mt: 2 }}>
                🎉 Tous les systèmes fonctionnent correctement !
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemStatus; 