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
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  Storage as StorageIcon,
  Psychology as PsychologyIcon,
  Rule as RuleIcon,
  Build as ToolsIcon,
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
            🧠 Système Cognitif Générique & Réflexif - Interface d'Administration
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
              variant="fullWidth"
              sx={{ 
                '& .MuiTab-root': { 
                  minWidth: 'auto',
                  fontSize: '0.875rem',
                  padding: '8px 12px'
                }
              }}
            >
              <Tab icon={<DashboardIcon />} label="Dashboard" {...a11yProps(0)} />
              <Tab icon={<SettingsIcon />} label="Configuration" {...a11yProps(1)} />
              <Tab icon={<PsychologyIcon />} label="Assistants LLM" {...a11yProps(2)} />
              <Tab icon={<MonitorIcon />} label="Interface RAG" {...a11yProps(3)} />
              <Tab icon={<ToolsIcon />} label="Outils & MCP" {...a11yProps(4)} />
              <Tab icon={<StorageIcon />} label="Base de Connaissances" {...a11yProps(5)} />
              <Tab icon={<RuleIcon />} label="Moteur de Règles" {...a11yProps(6)} />
            </Tabs>
          </Box>

          {/* Dashboard Tab */}
          <TabPanel value={tabValue} index={0}>
            <SystemStatus />
          </TabPanel>

          {/* Configuration Tab */}
          <TabPanel value={tabValue} index={1}>
            <ConfigurationManager />
          </TabPanel>

          {/* Assistants LLM Tab */}
          <TabPanel value={tabValue} index={2}>
            <LLMWorkflowGenerator />
          </TabPanel>

          {/* Interface RAG Tab */}
          <TabPanel value={tabValue} index={3}>
            <RAGChatInterface />
          </TabPanel>

          {/* Outils & MCP Tab */}
          <TabPanel value={tabValue} index={4}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      🔌 Serveur MCP
                    </Typography>
                    <MCPManager />
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      🛠️ Outils API
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
            </Grid>
          </TabPanel>

          {/* Base de Connaissances Tab */}
          <TabPanel value={tabValue} index={5}>
            <OntologyManager />
          </TabPanel>

          {/* Moteur de Règles Tab */}
          <TabPanel value={tabValue} index={6}>
            <RuleEngineManager />
          </TabPanel>
        </Paper>
      </Container>
    </Box>
  );
};

export default Layout; 