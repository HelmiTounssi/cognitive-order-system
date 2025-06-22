import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  TextField,
  Grid,
  Tabs,
  Tab,
  Paper,
  Alert,
  CircularProgress,
  Divider,
  CardActions,
  AppBar,
  Toolbar,
  Container
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Storage as StorageIcon,
  Psychology as PsychologyIcon,
  Rule as RuleIcon,
  Api as ApiIcon,
  Folder as ConfigurationIcon,
  AutoAwesome as LLMIcon,
  Chat as ChatIcon,
  Monitor as MonitorIcon
} from '@mui/icons-material';
import RuleEngineManager from './RuleEngineManager';
import ConfigurationManager from './ConfigurationManager';
import OntologyManager from './OntologyManager';
import LLMWorkflowGenerator from './LLMWorkflowGenerator';
import RAGChatInterface from './RAGChatInterface';
import SystemStatus from './SystemStatus';
import MCPManager from './MCPManager';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

const Layout: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [systemStatus, setSystemStatus] = useState({
    knowledgeBase: 'Opérationnel',
    vectorStore: 'Opérationnel',
    llmInterface: 'Opérationnel',
    agent: 'Opérationnel',
    ruleEngine: 'Opérationnel'
  });
  const [testQuery, setTestQuery] = useState('');

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Opérationnel': return 'success';
      case 'En cours': return 'warning';
      case 'Erreur': return 'error';
      default: return 'info';
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Système de Gestion Cognitif - Interface d'Administration
          </Typography>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="xl" sx={{ mt: 3 }}>
        <Paper sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange} 
              aria-label="admin tabs"
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab icon={<SettingsIcon />} label="Configuration" {...a11yProps(0)} />
              <Tab icon={<StorageIcon />} label="Base de Connaissances" {...a11yProps(1)} />
              <Tab icon={<PsychologyIcon />} label="Agent IA" {...a11yProps(2)} />
              <Tab icon={<RuleIcon />} label="Moteur de Règles" {...a11yProps(3)} />
              <Tab icon={<ApiIcon />} label="API & Outils" {...a11yProps(4)} />
              <Tab icon={<ConfigurationIcon />} label="Configurations" {...a11yProps(5)} />
              <Tab icon={<LLMIcon />} label="Assistants LLM" {...a11yProps(6)} />
              <Tab icon={<ChatIcon />} label="RAG Chat" {...a11yProps(7)} />
              <Tab icon={<MonitorIcon />} label="MCP" {...a11yProps(8)} />
            </Tabs>
          </Box>

          {/* Configuration Tab */}
          <TabPanel value={tabValue} index={0}>
            <SystemStatus />
          </TabPanel>

          {/* Knowledge Base Tab */}
          <TabPanel value={tabValue} index={1}>
            <OntologyManager />
          </TabPanel>

          {/* AI Agent Tab */}
          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Agent IA - Statut
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <CircularProgress size={20} />
                      <Typography>Agent en cours d'exécution</Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      L'agent traite actuellement les requêtes et effectue les inférences sémantiques.
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Button variant="contained" color="success">
                        Démarrer
                      </Button>
                      <Button variant="contained" color="error">
                        Arrêter
                      </Button>
                      <Button variant="outlined">
                        Redémarrer
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Logs de l'Agent
                    </Typography>
                    <Box sx={{ 
                      bgcolor: 'grey.100', 
                      p: 2, 
                      borderRadius: 1, 
                      maxHeight: 200, 
                      overflow: 'auto',
                      fontFamily: 'monospace',
                      fontSize: '0.875rem'
                    }}>
                      <div>[2024-01-15 10:30:15] Agent démarré</div>
                      <div>[2024-01-15 10:30:16] Base de connaissances chargée</div>
                      <div>[2024-01-15 10:30:17] Vector store initialisé</div>
                      <div>[2024-01-15 10:30:18] Interface LLM connectée</div>
                      <div>[2024-01-15 10:30:19] Moteur de règles initialisé</div>
                      <div>[2024-01-15 10:30:20] Prêt à traiter les requêtes</div>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Rule Engine Tab */}
          <TabPanel value={tabValue} index={3}>
            <RuleEngineManager />
          </TabPanel>
          
          {/* API & Tools Tab */}
          <TabPanel value={tabValue} index={4}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Outils Simulés
                    </Typography>
                    <List>
                      <ListItem>
                        <ListItemText 
                          primary="Gestion de Stock" 
                          secondary="Simulation d'API de stock"
                        />
                        <Button 
                          size="small" 
                          variant="outlined"
                          onClick={async () => {
                            try {
                              const response = await fetch('http://localhost:5001/api/tools/stock', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ action: 'check_stock', product_id: 'TEST-001' })
                              });
                              const result = await response.json();
                              alert(`Test Stock: ${result.success ? 'OK' : 'Erreur'}\n${JSON.stringify(result, null, 2)}`);
                            } catch (error) {
                              alert(`Erreur de connexion: ${error}`);
                            }
                          }}
                        >
                          Tester
                        </Button>
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Paiement" 
                          secondary="Simulation d'API de paiement"
                        />
                        <Button 
                          size="small" 
                          variant="outlined"
                          onClick={async () => {
                            try {
                              const response = await fetch('http://localhost:5001/api/tools/payment', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ action: 'process_payment', amount: 50.00 })
                              });
                              const result = await response.json();
                              alert(`Test Paiement: ${result.success ? 'OK' : 'Erreur'}\n${JSON.stringify(result, null, 2)}`);
                            } catch (error) {
                              alert(`Erreur de connexion: ${error}`);
                            }
                          }}
                        >
                          Tester
                        </Button>
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Livraison" 
                          secondary="Simulation d'API de livraison"
                        />
                        <Button 
                          size="small" 
                          variant="outlined"
                          onClick={async () => {
                            try {
                              const response = await fetch('http://localhost:5001/api/tools/delivery', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ action: 'check_delivery', address: 'Paris, France' })
                              });
                              const result = await response.json();
                              alert(`Test Livraison: ${result.success ? 'OK' : 'Erreur'}\n${JSON.stringify(result, null, 2)}`);
                            } catch (error) {
                              alert(`Erreur de connexion: ${error}`);
                            }
                          }}
                        >
                          Tester
                        </Button>
                      </ListItem>
                    </List>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Test de Requête
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={4}
                      label="Requête en langage naturel"
                      placeholder="Ex: Je veux commander 2 produits avec livraison express"
                      margin="normal"
                      value={testQuery}
                      onChange={(e) => setTestQuery(e.target.value)}
                    />
                    <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                      <Button 
                        variant="contained" 
                        color="primary"
                        onClick={async () => {
                          if (!testQuery.trim()) {
                            alert('Veuillez saisir une requête');
                            return;
                          }
                          try {
                            const response = await fetch('http://localhost:5001/api/rules/test', {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ query: testQuery })
                            });
                            const result = await response.json();
                            if (result.success) {
                              let message = `Test réussi!\n`;
                              message += `Intention: ${result.result.intent}\n`;
                              message += `Confiance: ${result.result.confidence}\n\n`;
                              message += `Actions exécutées (${result.result.executed_actions.length}):\n`;
                              
                              result.result.executed_actions.forEach((action: any, index: number) => {
                                message += `${index + 1}. ${action.action} (règle: ${action.rule})\n`;
                                if (action.result && action.result.status) {
                                  message += `   → ${action.result.status}\n`;
                                }
                              });
                              
                              if (result.result.entities) {
                                const entities = result.result.entities;
                                const entityList = Object.entries(entities)
                                  .filter(([key, value]) => value !== null && value !== undefined)
                                  .map(([key, value]) => `${key}: ${value}`)
                                  .join(', ');
                                
                                if (entityList) {
                                  message += `\nEntités détectées: ${entityList}`;
                                }
                              }
                              
                              alert(message);
                            } else {
                              alert(`Erreur: ${result.error}`);
                            }
                          } catch (error) {
                            alert(`Erreur de connexion: ${error}`);
                          }
                        }}
                      >
                        Envoyer
                      </Button>
                      <Button 
                        variant="outlined"
                        onClick={() => setTestQuery('')}
                      >
                        Effacer
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Configurations Tab */}
          <TabPanel value={tabValue} index={5}>
            <ConfigurationManager />
          </TabPanel>

          {/* LLM Workflow Generator Tab */}
          <TabPanel value={tabValue} index={6}>
            <LLMWorkflowGenerator />
          </TabPanel>

          {/* RAG Chat Tab */}
          <TabPanel value={tabValue} index={7}>
            <RAGChatInterface />
          </TabPanel>

          {/* MCP Tab */}
          <TabPanel value={tabValue} index={8}>
            <MCPManager />
          </TabPanel>
        </Paper>
      </Container>
    </Box>
  );
};

export default Layout; 