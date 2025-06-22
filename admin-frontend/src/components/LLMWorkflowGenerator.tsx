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
  DialogActions
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
  const [saveDialogData, setSaveDialogData] = useState({
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
        setError(data.error || 'Erreur lors de la génération du workflow');
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
        setError(data.error || 'Erreur lors de la génération des patterns');
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
        body: JSON.stringify({
          business_scenario: ruleData.business_scenario,
          constraints: ruleData.constraints.split('\n').filter(c => c.trim())
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setGeneratedRules(data.rules);
        setSuccess('Règles générées avec succès');
      } else {
        setError(data.error || 'Erreur lors de la génération des règles');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const openSaveDialog = (type: 'workflow' | 'patterns' | 'rules') => {
    setSaveDialogType(type);
    setSaveDialogData({
      name: `${type}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}`,
      description: `${type.charAt(0).toUpperCase() + type.slice(1)} généré par assistant LLM`,
      domain: type === 'workflow' ? workflowData.domain : 'generic'
    });
    setSaveDialogOpen(true);
  };

  const saveItem = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let endpoint = '';
      let data = {};
      
      switch (saveDialogType) {
        case 'workflow':
          endpoint = '/api/llm/save_workflow';
          data = {
            workflow: generatedWorkflow,
            metadata: saveDialogData
          };
          break;
        case 'patterns':
          endpoint = '/api/llm/save_patterns';
          data = {
            patterns: generatedPatterns,
            metadata: saveDialogData
          };
          break;
        case 'rules':
          endpoint = '/api/llm/save_rules';
          data = {
            rules: generatedRules,
            metadata: saveDialogData
          };
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
        setSuccess(responseData.message);
        setSaveDialogOpen(false);
        await loadSavedItems(); // Recharger la liste
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
        body: JSON.stringify({
          input_data: { test: 'data' }
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setSuccess(`Workflow "${data.workflow_name}" appliqué avec succès`);
      } else {
        setError(data.error || 'Erreur lors de l\'application du workflow');
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
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" gutterBottom>
        Assistants LLM - Générateur de Workflows
      </Typography>
      
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

      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="LLM assistants tabs">
          <Tab label="Configuration" />
          <Tab label="Génération de Workflow" />
          <Tab label="Génération de Patterns" />
          <Tab label="Génération de Règles" />
          <Tab icon={<ListIcon />} label="Éléments Sauvegardés" />
        </Tabs>
      </Paper>

      {/* Configuration Tab */}
      <TabPanel value={tabValue} index={0}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Configuration des Assistants LLM
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Clé API OpenAI"
                  type="password"
                  value={config.api_key}
                  onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="Modèle"
                  value={config.model}
                  onChange={(e) => setConfig({ ...config, model: e.target.value })}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="Température"
                  type="number"
                  inputProps={{ min: 0, max: 2, step: 0.1 }}
                  value={config.temperature}
                  onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })}
                  margin="normal"
                />
              </Grid>
            </Grid>
            
            <Button
              variant="contained"
              startIcon={<Settings />}
              onClick={configureAssistants}
              disabled={loading || !config.api_key}
              sx={{ mt: 2 }}
            >
              {loading ? <CircularProgress size={20} /> : 'Configurer'}
            </Button>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="h6" gutterBottom>
              Statut des Assistants
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Chip
                  icon={assistantsStatus.workflow_generator ? <CheckCircle /> : <Error />}
                  label="Générateur de Workflow"
                  color={assistantsStatus.workflow_generator ? 'success' : 'error'}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Chip
                  icon={assistantsStatus.pattern_generator ? <CheckCircle /> : <Error />}
                  label="Générateur de Patterns"
                  color={assistantsStatus.pattern_generator ? 'success' : 'error'}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Chip
                  icon={assistantsStatus.rule_generator ? <CheckCircle /> : <Error />}
                  label="Générateur de Règles"
                  color={assistantsStatus.rule_generator ? 'success' : 'error'}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Workflow Generation Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Génération de Workflow
                </Typography>
                
                <TextField
                  fullWidth
                  label="Domaine métier"
                  value={workflowData.domain}
                  onChange={(e) => setWorkflowData({ ...workflowData, domain: e.target.value })}
                  margin="normal"
                  placeholder="ex: e-commerce, santé, finance..."
                />
                
                <TextField
                  fullWidth
                  label="Contexte métier"
                  multiline
                  rows={4}
                  value={workflowData.business_context}
                  onChange={(e) => setWorkflowData({ ...workflowData, business_context: e.target.value })}
                  margin="normal"
                  placeholder="Décrivez le contexte métier et les objectifs..."
                />
                
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={generateWorkflow}
                  disabled={loading || !workflowData.domain || !workflowData.business_context}
                  sx={{ mt: 2 }}
                >
                  {loading ? <CircularProgress size={20} /> : 'Générer Workflow'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Workflow Généré
                </Typography>
                
                {generatedWorkflow ? (
                  <Box>
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Tooltip title="Copier">
                        <IconButton onClick={() => copyToClipboard(JSON.stringify(generatedWorkflow, null, 2))}>
                          <ContentCopy />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Télécharger">
                        <IconButton onClick={() => downloadResult(generatedWorkflow, 'workflow.json')}>
                          <Download />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Sauvegarder">
                        <IconButton 
                          onClick={() => openSaveDialog('workflow')}
                          color="primary"
                        >
                          <Save />
                        </IconButton>
                      </Tooltip>
                    </Box>
                    
                    <Paper sx={{ p: 2, maxHeight: 400, overflow: 'auto' }}>
                      <pre style={{ margin: 0, fontSize: '12px' }}>
                        {JSON.stringify(generatedWorkflow, null, 2)}
                      </pre>
                    </Paper>
                  </Box>
                ) : (
                  <Typography color="text.secondary">
                    Aucun workflow généré
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Pattern Generation Tab */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Génération de Patterns d'Extraction
                </Typography>
                
                <TextField
                  fullWidth
                  label="Type d'entité"
                  value={patternData.entity_type}
                  onChange={(e) => setPatternData({ ...patternData, entity_type: e.target.value })}
                  margin="normal"
                  placeholder="ex: Client, Produit, Commande..."
                />
                
                <TextField
                  fullWidth
                  label="Données d'exemple"
                  multiline
                  rows={4}
                  value={patternData.sample_data}
                  onChange={(e) => setPatternData({ ...patternData, sample_data: e.target.value })}
                  margin="normal"
                  placeholder="Donnez des exemples de données à extraire..."
                />
                
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={generatePatterns}
                  disabled={loading || !patternData.entity_type || !patternData.sample_data}
                  sx={{ mt: 2 }}
                >
                  {loading ? <CircularProgress size={20} /> : 'Générer Patterns'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Patterns Générés
                </Typography>
                
                {generatedPatterns ? (
                  <Box>
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Tooltip title="Copier">
                        <IconButton onClick={() => copyToClipboard(JSON.stringify(generatedPatterns, null, 2))}>
                          <ContentCopy />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Télécharger">
                        <IconButton onClick={() => downloadResult(generatedPatterns, 'patterns.json')}>
                          <Download />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Sauvegarder">
                        <IconButton 
                          onClick={() => openSaveDialog('patterns')}
                          color="primary"
                        >
                          <Save />
                        </IconButton>
                      </Tooltip>
                    </Box>
                    
                    <Paper sx={{ p: 2, maxHeight: 400, overflow: 'auto' }}>
                      <pre style={{ margin: 0, fontSize: '12px' }}>
                        {JSON.stringify(generatedPatterns, null, 2)}
                      </pre>
                    </Paper>
                  </Box>
                ) : (
                  <Typography color="text.secondary">
                    Aucun pattern généré
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Rule Generation Tab */}
      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Génération de Règles Métier
                </Typography>
                
                <TextField
                  fullWidth
                  label="Scénario métier"
                  multiline
                  rows={4}
                  value={ruleData.business_scenario}
                  onChange={(e) => setRuleData({ ...ruleData, business_scenario: e.target.value })}
                  margin="normal"
                  placeholder="Décrivez le scénario métier pour lequel générer des règles..."
                />
                
                <TextField
                  fullWidth
                  label="Contraintes (une par ligne)"
                  multiline
                  rows={3}
                  value={ruleData.constraints}
                  onChange={(e) => setRuleData({ ...ruleData, constraints: e.target.value })}
                  margin="normal"
                  placeholder="Listez les contraintes métier..."
                />
                
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={generateRules}
                  disabled={loading || !ruleData.business_scenario}
                  sx={{ mt: 2 }}
                >
                  {loading ? <CircularProgress size={20} /> : 'Générer Règles'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Règles Générées
                </Typography>
                
                {generatedRules ? (
                  <Box>
                    <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                      <Tooltip title="Copier">
                        <IconButton onClick={() => copyToClipboard(JSON.stringify(generatedRules, null, 2))}>
                          <ContentCopy />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Télécharger">
                        <IconButton onClick={() => downloadResult(generatedRules, 'rules.json')}>
                          <Download />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Sauvegarder">
                        <IconButton 
                          onClick={() => openSaveDialog('rules')}
                          color="primary"
                        >
                          <Save />
                        </IconButton>
                      </Tooltip>
                    </Box>
                    
                    <Paper sx={{ p: 2, maxHeight: 400, overflow: 'auto' }}>
                      <pre style={{ margin: 0, fontSize: '12px' }}>
                        {JSON.stringify(generatedRules, null, 2)}
                      </pre>
                    </Paper>
                  </Box>
                ) : (
                  <Typography color="text.secondary">
                    Aucune règle générée
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Saved Items Tab */}
      <TabPanel value={tabValue} index={4}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Workflows Sauvegardés ({savedItems.workflows.length})
                </Typography>
                <List>
                  {savedItems.workflows.map((workflow: any) => (
                    <ListItem key={workflow.id}>
                      <ListItemText
                        primary={workflow.name}
                        secondary={workflow.description}
                      />
                      <IconButton
                        onClick={() => applyWorkflow(workflow.id)}
                        color="primary"
                      >
                        <PlayCircle />
                      </IconButton>
                    </ListItem>
                  ))}
                  {savedItems.workflows.length === 0 && (
                    <Typography color="text.secondary">
                      Aucun workflow sauvegardé
                    </Typography>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Patterns Sauvegardés ({savedItems.patterns.length})
                </Typography>
                <List>
                  {savedItems.patterns.map((pattern: any) => (
                    <ListItem key={pattern.id}>
                      <ListItemText
                        primary={pattern.name}
                        secondary={pattern.description}
                      />
                    </ListItem>
                  ))}
                  {savedItems.patterns.length === 0 && (
                    <Typography color="text.secondary">
                      Aucun pattern sauvegardé
                    </Typography>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Règles Sauvegardées ({savedItems.rules.length})
                </Typography>
                <List>
                  {savedItems.rules.map((rule: any) => (
                    <ListItem key={rule.id}>
                      <ListItemText
                        primary={rule.name}
                        secondary={rule.description}
                      />
                    </ListItem>
                  ))}
                  {savedItems.rules.length === 0 && (
                    <Typography color="text.secondary">
                      Aucune règle sauvegardée
                    </Typography>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Save Dialog */}
      <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)}>
        <DialogTitle>
          Sauvegarder {saveDialogType === 'workflow' ? 'le Workflow' : saveDialogType === 'patterns' ? 'les Patterns' : 'les Règles'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Nom"
            value={saveDialogData.name}
            onChange={(e) => setSaveDialogData({ ...saveDialogData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={2}
            value={saveDialogData.description}
            onChange={(e) => setSaveDialogData({ ...saveDialogData, description: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Domaine"
            value={saveDialogData.domain}
            onChange={(e) => setSaveDialogData({ ...saveDialogData, domain: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSaveDialogOpen(false)}>Annuler</Button>
          <Button 
            onClick={saveItem} 
            variant="contained"
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : 'Sauvegarder'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LLMWorkflowGenerator; 