import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Grid,
  Alert,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as TestIcon,
  Download as ExportIcon,
  Upload as ImportIcon,
  Assessment as StatsIcon
} from '@mui/icons-material';

interface Rule {
  name: string;
  description: string;
  conditions: string[];
  actions: string[];
  priority: number;
  category: string;
  enabled: boolean;
  created_at: string;
}

interface RuleTemplate {
  description: string;
  conditions: string[];
  actions: string[];
  priority: number;
  category: string;
}

interface RuleEngineManagerProps {
  apiBaseUrl?: string;
}

const RuleEngineManager: React.FC<RuleEngineManagerProps> = ({ 
  apiBaseUrl = 'http://localhost:5001' 
}) => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [templates, setTemplates] = useState<Record<string, RuleTemplate>>({});
  const [categories, setCategories] = useState<Record<string, number>>({});
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog states
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [testQuery, setTestQuery] = useState('');
  const [testResult, setTestResult] = useState<any>(null);
  
  // Form states
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    conditions: [''],
    actions: [''],
    priority: 1,
    category: '',
    enabled: true
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [rulesRes, templatesRes, categoriesRes, statsRes] = await Promise.all([
        fetch(`${apiBaseUrl}/api/rules`),
        fetch(`${apiBaseUrl}/api/rules/templates`),
        fetch(`${apiBaseUrl}/api/rules/categories`),
        fetch(`${apiBaseUrl}/api/rules/statistics`)
      ]);

      if (rulesRes.ok) {
        const rulesData = await rulesRes.json();
        setRules(rulesData.rules || []);
      }

      if (templatesRes.ok) {
        const templatesData = await templatesRes.json();
        setTemplates(templatesData.templates || {});
      }

      if (categoriesRes.ok) {
        const categoriesData = await categoriesRes.json();
        setCategories(categoriesData.categories || {});
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStatistics(statsData.statistics);
      }
    } catch (err) {
      setError('Erreur lors du chargement des données');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/rules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setDialogOpen(false);
        resetForm();
        loadData();
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de la création');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleUpdateRule = async () => {
    if (!editingRule) return;

    try {
      const response = await fetch(`${apiBaseUrl}/api/rules/${editingRule.name}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setDialogOpen(false);
        setEditingRule(null);
        resetForm();
        loadData();
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de la mise à jour');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleDeleteRule = async (ruleName: string) => {
    if (!window.confirm(`Supprimer la règle "${ruleName}" ?`)) return;

    try {
      const response = await fetch(`${apiBaseUrl}/api/rules/${ruleName}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        loadData();
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de la suppression');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleTestRule = async () => {
    if (!testQuery.trim()) return;

    try {
      const response = await fetch(`${apiBaseUrl}/api/rules/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: testQuery })
      });

      if (response.ok) {
        const result = await response.json();
        setTestResult(result.result);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors du test');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleExportRules = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/rules/export`);
      if (response.ok) {
        const data = await response.json();
        const blob = new Blob([data.data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'rules_export.json';
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      setError('Erreur lors de l\'export');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      conditions: [''],
      actions: [''],
      priority: 1,
      category: '',
      enabled: true
    });
  };

  const openEditDialog = (rule: Rule) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      description: rule.description,
      conditions: [...rule.conditions],
      actions: [...rule.actions],
      priority: rule.priority,
      category: rule.category,
      enabled: rule.enabled
    });
    setDialogOpen(true);
  };

  const openCreateDialog = () => {
    setEditingRule(null);
    resetForm();
    setDialogOpen(true);
  };

  const addCondition = () => {
    setFormData(prev => ({
      ...prev,
      conditions: [...prev.conditions, '']
    }));
  };

  const removeCondition = (index: number) => {
    setFormData(prev => ({
      ...prev,
      conditions: prev.conditions.filter((_, i) => i !== index)
    }));
  };

  const updateCondition = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      conditions: prev.conditions.map((c, i) => i === index ? value : c)
    }));
  };

  const addAction = () => {
    setFormData(prev => ({
      ...prev,
      actions: [...prev.actions, '']
    }));
  };

  const removeAction = (index: number) => {
    setFormData(prev => ({
      ...prev,
      actions: prev.actions.filter((_, i) => i !== index)
    }));
  };

  const updateAction = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      actions: prev.actions.map((a, i) => i === index ? value : a)
    }));
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={3}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Header avec statistiques */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Moteur de Règles</Typography>
            <Box>
              <Button
                startIcon={<AddIcon />}
                variant="contained"
                onClick={openCreateDialog}
                sx={{ mr: 1 }}
              >
                Nouvelle Règle
              </Button>
              <Button
                startIcon={<TestIcon />}
                variant="outlined"
                onClick={() => setTestDialogOpen(true)}
                sx={{ mr: 1 }}
              >
                Tester
              </Button>
              <Button
                startIcon={<ExportIcon />}
                variant="outlined"
                onClick={handleExportRules}
              >
                Exporter
              </Button>
            </Box>
          </Box>

          {statistics && (
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Règles Totales
                </Typography>
                <Typography variant="h4">
                  {statistics.business_rules?.total || 0}
                </Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Règles Activées
                </Typography>
                <Typography variant="h4">
                  {statistics.business_rules?.enabled || 0}
                </Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Inférences
                </Typography>
                <Typography variant="h4">
                  {statistics.rule_engine?.total_inferences || 0}
                </Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="subtitle2" color="text.secondary">
                  Confiance Moyenne
                </Typography>
                <Typography variant="h4">
                  {statistics.rule_engine?.performance_metrics?.avg_confidence?.toFixed(2) || '0.00'}
                </Typography>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>

      {/* Liste des règles */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Règles Métier ({rules.length})
          </Typography>
          
          <List>
            {rules.map((rule, index) => (
              <React.Fragment key={rule.name}>
                <ListItem>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle1">{rule.name}</Typography>
                        <Chip 
                          label={rule.category} 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                        />
                        <Chip 
                          label={`Priorité: ${rule.priority}`} 
                          size="small" 
                          color="secondary" 
                          variant="outlined"
                        />
                        <Switch 
                          checked={rule.enabled} 
                          size="small" 
                          disabled
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          {rule.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Conditions: {rule.conditions.join(', ')}
                        </Typography>
                        <br />
                        <Typography variant="caption" color="text.secondary">
                          Actions: {rule.actions.join(', ')}
                        </Typography>
                      </Box>
                    }
                  />
                  <ListItemSecondaryAction>
                    <IconButton onClick={() => openEditDialog(rule)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton onClick={() => handleDeleteRule(rule.name)}>
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
                {index < rules.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Dialog de création/édition de règle */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingRule ? 'Modifier la Règle' : 'Nouvelle Règle'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Nom de la règle"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                disabled={!!editingRule}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Catégorie</InputLabel>
                <Select
                  value={formData.category}
                  onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                  label="Catégorie"
                >
                  {Object.keys(templates).map(cat => (
                    <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Priorité"
                type="number"
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: parseInt(e.target.value) }))}
                inputProps={{ min: 1, max: 10 }}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.enabled}
                    onChange={(e) => setFormData(prev => ({ ...prev, enabled: e.target.checked }))}
                  />
                }
                label="Activée"
              />
            </Grid>
            
            {/* Conditions */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Conditions
              </Typography>
              {formData.conditions.map((condition, index) => (
                <Box key={index} display="flex" gap={1} mb={1}>
                  <TextField
                    fullWidth
                    label={`Condition ${index + 1}`}
                    value={condition}
                    onChange={(e) => updateCondition(index, e.target.value)}
                    placeholder="ex: intent:commander"
                  />
                  <IconButton onClick={() => removeCondition(index)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
              <Button onClick={addCondition} startIcon={<AddIcon />}>
                Ajouter une condition
              </Button>
            </Grid>

            {/* Actions */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Actions
              </Typography>
              {formData.actions.map((action, index) => (
                <Box key={index} display="flex" gap={1} mb={1}>
                  <TextField
                    fullWidth
                    label={`Action ${index + 1}`}
                    value={action}
                    onChange={(e) => updateAction(index, e.target.value)}
                    placeholder="ex: validate_order"
                  />
                  <IconButton onClick={() => removeAction(index)} color="error">
                    <DeleteIcon />
                  </IconButton>
                </Box>
              ))}
              <Button onClick={addAction} startIcon={<AddIcon />}>
                Ajouter une action
              </Button>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Annuler</Button>
          <Button 
            onClick={editingRule ? handleUpdateRule : handleCreateRule}
            variant="contained"
          >
            {editingRule ? 'Mettre à jour' : 'Créer'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de test */}
      <Dialog open={testDialogOpen} onClose={() => setTestDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Tester le Moteur de Règles</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Requête en langage naturel"
            value={testQuery}
            onChange={(e) => setTestQuery(e.target.value)}
            multiline
            rows={3}
            placeholder="Ex: Je veux commander 3 produits avec livraison express"
            sx={{ mb: 2, mt: 1 }}
          />
          
          {testResult && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Résultat du test:
              </Typography>
              <Box 
                sx={{ 
                  bgcolor: 'grey.100', 
                  p: 2, 
                  borderRadius: 1,
                  fontFamily: 'monospace',
                  fontSize: '0.875rem'
                }}
              >
                <pre>{JSON.stringify(testResult, null, 2)}</pre>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialogOpen(false)}>Fermer</Button>
          <Button onClick={handleTestRule} variant="contained">
            Tester
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RuleEngineManager; 