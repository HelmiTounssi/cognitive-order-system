import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Tabs,
  Tab,
  Paper,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem
} from '@mui/material';
import {
  PlayArrow,
  Settings,
  CheckCircle,
  Error,
  ExpandMore,
  ContentCopy,
  Download,
  Upload,
  Save,
  List as ListIcon,
  PlayCircle
} from '@mui/icons-material';

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
      id={`llm-tabpanel-${index}`}
      aria-labelledby={`llm-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface LLMWorkflowGeneratorProps {
  // Props si nécessaire
}

const LLMWorkflowGenerator: React.FC<LLMWorkflowGeneratorProps> = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // État pour la configuration
  const [config, setConfig] = useState({
    api_key: '',
    model: 'gpt-4',
    temperature: 0.7
  });
  
  // État pour les assistants
  const [assistantsStatus, setAssistantsStatus] = useState({
    workflow_generator: false,
    pattern_generator: false,
    rule_generator: false
  });
  
  // État pour la génération de workflow
  const [workflowData, setWorkflowData] = useState({
    domain: '',
    business_context: ''
  });
  const [generatedWorkflow, setGeneratedWorkflow] = useState<any>(null);
  
  // État pour la génération de patterns
  const [patternData, setPatternData] = useState({
    entity_type: '',
    sample_data: ''
  });
  const [generatedPatterns, setGeneratedPatterns] = useState<any>(null);
  
  // État pour la génération de règles
  const [ruleData, setRuleData] = useState({
    business_scenario: '',
    constraints: ''
  });
  const [generatedRules, setGeneratedRules] = useState<any>(null);

  // État pour les éléments sauvegardés
  const [savedItems, setSavedItems] = useState({
    workflows: [],
    patterns: [],
    rules: []
  });

  // État pour les dialogues de sauvegarde
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [saveDialogType, setSaveDialogType] = useState<'workflow' | 'patterns' | 'rules'>('workflow');
  const [saveDialogData, setSaveDialogData] = useState<{
    name: string;
    description: string;
    domain: string;
    workflow?: any;
    patterns?: any;
    rules?: any;
  }>({
    name: '',
    description: '',
    domain: ''
  });

  useEffect(() => {
    checkAssistantsStatus();
    loadSavedItems();
  }, []);

  const checkAssistantsStatus = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/llm/assistants/status');
      const data = await response.json();
      
      if (data.success) {
        setAssistantsStatus(data.status);
      }
    } catch (error) {
      console.error('Erreur lors de la vérification du statut:', error);
    }
  };

  const loadSavedItems = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/llm/saved_items');
      const data = await response.json();
      
      if (data.success) {
        setSavedItems(data.items);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des éléments sauvegardés:', error);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const configureAssistants = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/llm/assistants/configure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSuccess('Assistants LLM configurés avec succès');
        await checkAssistantsStatus();
      } else {
        setError(data.error || 'Erreur lors de la configuration');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const generateWorkflow = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/llm/generate_workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowData),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setGeneratedWorkflow(data.workflow);
        setSuccess('Workflow généré avec succès');
      } else {
        setError(data.error || 'Erreur lors de la génération');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const generatePatterns = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/llm/generate_patterns', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(patternData),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setGeneratedPatterns(data.patterns);
        setSuccess('Patterns générés avec succès');
      } else {
        setError(data.error || 'Erreur lors de la génération');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const generateRules = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:5001/api/llm/generate_rules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(ruleData),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setGeneratedRules(data.rules);
        setSuccess('Règles générées avec succès');
      } else {
        setError(data.error || 'Erreur lors de la génération');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const openSaveDialog = (type: 'workflow' | 'patterns' | 'rules') => {
    setSaveDialogType(type);
    setSaveDialogData({ name: '', description: '', domain: '' });
    setSaveDialogOpen(true);
  };

  const saveItem = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let endpoint = '';
      let data = { ...saveDialogData };
      
      switch (saveDialogType) {
        case 'workflow':
          endpoint = '/api/llm/save_workflow';
          data.workflow = generatedWorkflow;
          break;
        case 'patterns':
          endpoint = '/api/llm/save_patterns';
          data.patterns = generatedPatterns;
          break;
        case 'rules':
          endpoint = '/api/llm/save_rules';
          data.rules = generatedRules;
          break;
      }
      
      const response = await fetch(`http://localhost:5001${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      const responseData = await response.json();
      
      if (responseData.success) {
        setSuccess(`${saveDialogType === 'workflow' ? 'Workflow' : saveDialogType === 'patterns' ? 'Patterns' : 'Règles'} sauvegardé avec succès`);
        setSaveDialogOpen(false);
        await loadSavedItems();
      } else {
        setError(responseData.error || 'Erreur lors de la sauvegarde');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const applyWorkflow = async (workflowId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:5001/api/llm/apply_workflow/${workflowId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSuccess('Workflow appliqué avec succès');
      } else {
        setError(data.error || 'Erreur lors de l\'application');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copié dans le presse-papiers');
  };

  const downloadResult = (content: any, filename: string) => {
    const blob = new Blob([JSON.stringify(content, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header avec statut */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ py: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">🤖 Assistants IA & Génération</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {Object.entries(assistantsStatus).map(([key, status]) => (
                <Chip
                  key={key}
                  label={key.replace('_', ' ')}
                  color={status ? 'success' : 'default'}
                  size="small"
                  variant={status ? 'filled' : 'outlined'}
                />
              ))}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Messages d'état */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Interface principale */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        {/* Contenu principal */}
        <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
            <Tabs value={tabValue} onChange={handleTabChange} sx={{ 
              borderBottom: 1, 
              borderColor: 'divider',
              '& .MuiTab-root': { 
                minWidth: 'auto',
                fontSize: '0.8rem',
                padding: '6px 8px'
              }
            }}>
              <Tab label="🔄 Workflows" />
              <Tab label="📋 Patterns" />
              <Tab label="⚖️ Règles" />
              <Tab label="💾 Sauvegardés" />
            </Tabs>

            <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2, maxWidth: '100%' }}>
              {/* Tab Workflows */}
              <TabPanel value={tabValue} index={0}>
                <Grid container spacing={2}>
                  <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 2, height: 'fit-content' }}>
                      <Typography variant="h6" gutterBottom>Générer un Workflow</Typography>
                      <TextField
                        label="Domaine métier"
                        value={workflowData.domain}
                        onChange={(e) => setWorkflowData({ ...workflowData, domain: e.target.value })}
                        fullWidth
                        size="small"
                        sx={{ mb: 2 }}
                      />
                      <TextField
                        label="Contexte métier"
                        value={workflowData.business_context}
                        onChange={(e) => setWorkflowData({ ...workflowData, business_context: e.target.value })}
                        fullWidth
                        multiline
                        rows={3}
                        size="small"
                        sx={{ mb: 2 }}
                      />
                      <Button
                        variant="contained"
                        onClick={generateWorkflow}
                        disabled={loading}
                        fullWidth
                      >
                        {loading ? <CircularProgress size={20} /> : 'Générer'}
                      </Button>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 2, height: 'fit-content' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">Résultat</Typography>
                        {generatedWorkflow && (
                          <Box>
                            <IconButton onClick={() => copyToClipboard(JSON.stringify(generatedWorkflow, null, 2))} size="small">
                              <ContentCopy />
                            </IconButton>
                            <IconButton onClick={() => downloadResult(generatedWorkflow, 'workflow.json')} size="small">
                              <Download />
                            </IconButton>
                            <Button size="small" onClick={() => openSaveDialog('workflow')}>
                              <Save />
                            </Button>
                          </Box>
                        )}
                      </Box>
                      {generatedWorkflow ? (
                        <Box sx={{ maxHeight: 400, overflow: 'auto', wordBreak: 'break-word' }}>
                          <pre style={{ fontSize: '0.75rem', margin: 0, whiteSpace: 'pre-wrap' }}>
                            {JSON.stringify(generatedWorkflow, null, 2)}
                          </pre>
                        </Box>
                      ) : (
                        <Typography color="text.secondary">Aucun workflow généré</Typography>
                      )}
                    </Paper>
                  </Grid>
                </Grid>
              </TabPanel>

              {/* Tab Patterns */}
              <TabPanel value={tabValue} index={1}>
                <Grid container spacing={2}>
                  <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 2, height: 'fit-content' }}>
                      <Typography variant="h6" gutterBottom>Générer des Patterns</Typography>
                      <TextField
                        label="Type d'entité"
                        value={patternData.entity_type}
                        onChange={(e) => setPatternData({ ...patternData, entity_type: e.target.value })}
                        fullWidth
                        size="small"
                        sx={{ mb: 2 }}
                      />
                      <TextField
                        label="Données d'exemple"
                        value={patternData.sample_data}
                        onChange={(e) => setPatternData({ ...patternData, sample_data: e.target.value })}
                        fullWidth
                        multiline
                        rows={3}
                        size="small"
                        sx={{ mb: 2 }}
                      />
                      <Button
                        variant="contained"
                        onClick={generatePatterns}
                        disabled={loading}
                        fullWidth
                      >
                        {loading ? <CircularProgress size={20} /> : 'Générer'}
                      </Button>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 2, height: 'fit-content' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">Résultat</Typography>
                        {generatedPatterns && (
                          <Box>
                            <IconButton onClick={() => copyToClipboard(JSON.stringify(generatedPatterns, null, 2))} size="small">
                              <ContentCopy />
                            </IconButton>
                            <IconButton onClick={() => downloadResult(generatedPatterns, 'patterns.json')} size="small">
                              <Download />
                            </IconButton>
                            <Button size="small" onClick={() => openSaveDialog('patterns')}>
                              <Save />
                            </Button>
                          </Box>
                        )}
                      </Box>
                      {generatedPatterns ? (
                        <Box sx={{ maxHeight: 400, overflow: 'auto', wordBreak: 'break-word' }}>
                          <pre style={{ fontSize: '0.75rem', margin: 0, whiteSpace: 'pre-wrap' }}>
                            {JSON.stringify(generatedPatterns, null, 2)}
                          </pre>
                        </Box>
                      ) : (
                        <Typography color="text.secondary">Aucun pattern généré</Typography>
                      )}
                    </Paper>
                  </Grid>
                </Grid>
              </TabPanel>

              {/* Tab Règles */}
              <TabPanel value={tabValue} index={2}>
                <Grid container spacing={2}>
                  <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 2, height: 'fit-content' }}>
                      <Typography variant="h6" gutterBottom>Générer des Règles</Typography>
                      <TextField
                        label="Scénario métier"
                        value={ruleData.business_scenario}
                        onChange={(e) => setRuleData({ ...ruleData, business_scenario: e.target.value })}
                        fullWidth
                        multiline
                        rows={3}
                        size="small"
                        sx={{ mb: 2 }}
                      />
                      <TextField
                        label="Contraintes"
                        value={ruleData.constraints}
                        onChange={(e) => setRuleData({ ...ruleData, constraints: e.target.value })}
                        fullWidth
                        multiline
                        rows={3}
                        size="small"
                        sx={{ mb: 2 }}
                      />
                      <Button
                        variant="contained"
                        onClick={generateRules}
                        disabled={loading}
                        fullWidth
                      >
                        {loading ? <CircularProgress size={20} /> : 'Générer'}
                      </Button>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} lg={6}>
                    <Paper sx={{ p: 2, height: 'fit-content' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">Résultat</Typography>
                        {generatedRules && (
                          <Box>
                            <IconButton onClick={() => copyToClipboard(JSON.stringify(generatedRules, null, 2))} size="small">
                              <ContentCopy />
                            </IconButton>
                            <IconButton onClick={() => downloadResult(generatedRules, 'rules.json')} size="small">
                              <Download />
                            </IconButton>
                            <Button size="small" onClick={() => openSaveDialog('rules')}>
                              <Save />
                            </Button>
                          </Box>
                        )}
                      </Box>
                      {generatedRules ? (
                        <Box sx={{ maxHeight: 400, overflow: 'auto', wordBreak: 'break-word' }}>
                          <pre style={{ fontSize: '0.75rem', margin: 0, whiteSpace: 'pre-wrap' }}>
                            {JSON.stringify(generatedRules, null, 2)}
                          </pre>
                        </Box>
                      ) : (
                        <Typography color="text.secondary">Aucune règle générée</Typography>
                      )}
                    </Paper>
                  </Grid>
                </Grid>
              </TabPanel>

              {/* Tab Sauvegardés */}
              <TabPanel value={tabValue} index={3}>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, maxHeight: 500, overflow: 'auto' }}>
                      <Typography variant="h6" gutterBottom>Workflows</Typography>
                      <List dense>
                        {savedItems.workflows.map((item: any) => (
                          <ListItem key={item.id} sx={{ flexDirection: 'column', alignItems: 'flex-start', p: 1 }}>
                            <ListItemText
                              primary={item.name}
                              secondary={item.description}
                              primaryTypographyProps={{ fontSize: '0.9rem' }}
                              secondaryTypographyProps={{ fontSize: '0.8rem' }}
                            />
                            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                              <Button size="small" onClick={() => applyWorkflow(item.id)}>
                                <PlayArrow />
                              </Button>
                              <IconButton size="small" onClick={() => copyToClipboard(JSON.stringify(item, null, 2))}>
                                <ContentCopy />
                              </IconButton>
                            </Box>
                          </ListItem>
                        ))}
                      </List>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, maxHeight: 500, overflow: 'auto' }}>
                      <Typography variant="h6" gutterBottom>Patterns</Typography>
                      <List dense>
                        {savedItems.patterns.map((item: any) => (
                          <ListItem key={item.id} sx={{ flexDirection: 'column', alignItems: 'flex-start', p: 1 }}>
                            <ListItemText
                              primary={item.name}
                              secondary={item.description}
                              primaryTypographyProps={{ fontSize: '0.9rem' }}
                              secondaryTypographyProps={{ fontSize: '0.8rem' }}
                            />
                            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                              <IconButton size="small" onClick={() => copyToClipboard(JSON.stringify(item, null, 2))}>
                                <ContentCopy />
                              </IconButton>
                            </Box>
                          </ListItem>
                        ))}
                      </List>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <Paper sx={{ p: 2, maxHeight: 500, overflow: 'auto' }}>
                      <Typography variant="h6" gutterBottom>Règles</Typography>
                      <List dense>
                        {savedItems.rules.map((item: any) => (
                          <ListItem key={item.id} sx={{ flexDirection: 'column', alignItems: 'flex-start', p: 1 }}>
                            <ListItemText
                              primary={item.name}
                              secondary={item.description}
                              primaryTypographyProps={{ fontSize: '0.9rem' }}
                              secondaryTypographyProps={{ fontSize: '0.8rem' }}
                            />
                            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                              <IconButton size="small" onClick={() => copyToClipboard(JSON.stringify(item, null, 2))}>
                                <ContentCopy />
                              </IconButton>
                            </Box>
                          </ListItem>
                        ))}
                      </List>
                    </Paper>
                  </Grid>
                </Grid>
              </TabPanel>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Dialogue de sauvegarde */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Sauvegarder {saveDialogType === 'workflow' ? 'le workflow' : saveDialogType === 'patterns' ? 'les patterns' : 'les règles'}</DialogTitle>
        <DialogContent>
          <TextField
            label="Nom"
            value={saveDialogData.name}
            onChange={(e) => setSaveDialogData({ ...saveDialogData, name: e.target.value })}
            fullWidth
            sx={{ mb: 2, mt: 1 }}
          />
          <TextField
            label="Description"
            value={saveDialogData.description}
            onChange={(e) => setSaveDialogData({ ...saveDialogData, description: e.target.value })}
            fullWidth
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
          <TextField
            label="Domaine"
            value={saveDialogData.domain}
            onChange={(e) => setSaveDialogData({ ...saveDialogData, domain: e.target.value })}
            fullWidth
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>Annuler</Button>
          <Button onClick={saveItem} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Sauvegarder'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LLMWorkflowGenerator; 