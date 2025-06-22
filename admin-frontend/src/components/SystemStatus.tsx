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
  Button
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
  Computer as ComputerIcon
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
  const [statusData, setStatusData] = useState<SystemStatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const API_BASE = 'http://localhost:5001/api';

  const fetchSystemStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE}/system/status`);
      const data = await response.json();
      
      if (data.success) {
        setStatusData(data);
        setLastUpdate(new Date());
      } else {
        setError(data.error || 'Erreur lors de la récupération du statut');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemStatus();
    
    // Rafraîchir automatiquement toutes les 30 secondes
    const interval = setInterval(fetchSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
      case 'online':
        return 'success';
      case 'good':
        return 'primary';
      case 'warning':
        return 'warning';
      case 'critical':
      case 'offline':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
      case 'online':
        return <CheckCircleIcon />;
      case 'good':
        return <InfoIcon />;
      case 'warning':
        return <WarningIcon />;
      case 'critical':
      case 'offline':
        return <ErrorIcon />;
      default:
        return <InfoIcon />;
    }
  };

  const formatBytes = (bytes: number) => {
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getComponentLabel = (component: string) => {
    const labels: { [key: string]: string } = {
      rule_engine: 'Moteur de Règles',
      knowledge_base: 'Base de Connaissances',
      vector_store: 'Base Vectorielle',
      llm_interface: 'Interface LLM',
      rag_system: 'Système RAG',
      config_manager: 'Gestionnaire de Config'
    };
    return labels[component] || component;
  };

  if (loading && !statusData) {
    return (
      <Box sx={{ p: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Statut du Système
            </Typography>
            <LinearProgress />
          </CardContent>
        </Card>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" action={
          <Button color="inherit" size="small" onClick={fetchSystemStatus}>
            Réessayer
          </Button>
        }>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!statusData) return null;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header avec statut global */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h5" component="h2">
              Statut du Système
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={getStatusIcon(statusData.system_status.global_status)}
                label={`${statusData.system_status.global_status.toUpperCase()} (${statusData.system_status.health_percentage}%)`}
                color={getStatusColor(statusData.system_status.global_status) as any}
                variant="outlined"
              />
              <Tooltip title="Rafraîchir">
                <IconButton onClick={fetchSystemStatus} disabled={loading}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={statusData.system_status.health_percentage}
            color={getStatusColor(statusData.system_status.global_status) as any}
            sx={{ height: 8, borderRadius: 4, mb: 2 }}
          />
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {statusData.system_status.online_components}/{statusData.system_status.total_components}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Composants Actifs
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {statusData.system_info.cpu_count}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  CPU Cores
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {statusData.system_info.memory_percent}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Utilisation RAM
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {statusData.system_info.disk_usage}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Utilisation Disque
                </Typography>
              </Box>
            </Grid>
          </Grid>
          
          {lastUpdate && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
              Dernière mise à jour: {lastUpdate.toLocaleTimeString()}
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Informations système détaillées */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              Informations Système
            </Typography>
            <IconButton onClick={() => setExpanded(!expanded)}>
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
          
          <Collapse in={expanded}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <ComputerIcon color="primary" />
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Plateforme
                    </Typography>
                    <Typography variant="body1">
                      {statusData.system_info.platform}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SpeedIcon color="primary" />
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Python
                    </Typography>
                    <Typography variant="body1">
                      {statusData.system_info.python_version}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <MemoryIcon color="primary" />
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      RAM Disponible
                    </Typography>
                    <Typography variant="body1">
                      {formatBytes(statusData.system_info.memory_available)}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <StorageIcon color="primary" />
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      RAM Totale
                    </Typography>
                    <Typography variant="body1">
                      {formatBytes(statusData.system_info.memory_total)}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Collapse>
        </CardContent>
      </Card>

      {/* Statut des composants */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Statut des Composants
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(statusData.components).map(([component, status]) => (
              <Grid item xs={12} sm={6} md={4} key={component}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="subtitle2">
                        {getComponentLabel(component)}
                      </Typography>
                      <Chip
                        icon={getStatusIcon(status.status)}
                        label={status.status}
                        color={getStatusColor(status.status) as any}
                        size="small"
                      />
                    </Box>
                    <List dense>
                      {Object.entries(status).map(([key, value]) => {
                        if (key === 'status') return null;
                        return (
                          <ListItem key={key} sx={{ py: 0 }}>
                            <ListItemText
                              primary={key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              secondary={typeof value === 'boolean' ? (value ? 'Oui' : 'Non') : value}
                            />
                          </ListItem>
                        );
                      })}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Recommandations */}
      {statusData.recommendations.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recommandations
            </Typography>
            <List>
              {statusData.recommendations.map((recommendation, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    {recommendation.includes('✅') ? (
                      <CheckCircleIcon color="success" />
                    ) : recommendation.includes('⚠️') ? (
                      <WarningIcon color="warning" />
                    ) : (
                      <InfoIcon color="info" />
                    )}
                  </ListItemIcon>
                  <ListItemText primary={recommendation} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default SystemStatus; 