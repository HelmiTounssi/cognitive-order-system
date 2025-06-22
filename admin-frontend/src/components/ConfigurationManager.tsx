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
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  Grid
} from '@mui/material';
import {
  Upload as UploadIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Settings as SettingsIcon,
  FileCopy as FileCopyIcon
} from '@mui/icons-material';

interface Configuration {
  filename: string;
  filepath: string;
  name: string;
  description: string;
  version: string;
  created_at: string;
  updated_at: string;
  format: string;
  size: number;
}

interface ConfigurationManagerProps {
  apiBaseUrl?: string;
}

const ConfigurationManager: React.FC<ConfigurationManagerProps> = ({ 
  apiBaseUrl = 'http://localhost:5001' 
}) => {
  const [configurations, setConfigurations] = useState<Configuration[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog states
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  // Form states
  const [exportForm, setExportForm] = useState({
    format: 'json',
    filename: ''
  });

  useEffect(() => {
    loadConfigurations();
  }, []);

  const loadConfigurations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiBaseUrl}/api/configurations`);
      if (response.ok) {
        const data = await response.json();
        setConfigurations(data.configurations || []);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors du chargement');
      }
    } catch (err) {
      setError('Erreur de connexion');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExportConfiguration = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/configurations/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(exportForm)
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Configuration exportée avec succès!\nFichier: ${result.filename}`);
        setExportDialogOpen(false);
        setExportForm({ format: 'json', filename: '' });
        loadConfigurations(); // Recharger la liste
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de l\'export');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleImportConfiguration = async () => {
    if (!selectedFile) {
      setError('Veuillez sélectionner un fichier');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${apiBaseUrl}/api/configurations/import`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Configuration importée avec succès!\nNom: ${result.config_name}\nVersion: ${result.version}`);
        setImportDialogOpen(false);
        setSelectedFile(null);
        loadConfigurations(); // Recharger la liste
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de l\'import');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleDownloadConfiguration = async (filename: string) => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/configurations/${filename}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors du téléchargement');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleDeleteConfiguration = async (filename: string) => {
    if (!window.confirm(`Supprimer la configuration "${filename}" ?`)) return;

    try {
      const response = await fetch(`${apiBaseUrl}/api/configurations/${filename}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        loadConfigurations(); // Recharger la liste
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de la suppression');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('fr-FR');
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

      {/* Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Gestionnaire de Configurations</Typography>
            <Box>
              <Button
                startIcon={<AddIcon />}
                variant="contained"
                onClick={() => setExportDialogOpen(true)}
                sx={{ mr: 1 }}
              >
                Exporter Configuration
              </Button>
              <Button
                startIcon={<UploadIcon />}
                variant="outlined"
                onClick={() => setImportDialogOpen(true)}
              >
                Importer Configuration
              </Button>
            </Box>
          </Box>

          <Typography variant="body2" color="text.secondary">
            Gérez les configurations métier complètes du système (règles, ontologie, paramètres)
          </Typography>
        </CardContent>
      </Card>

      {/* Liste des configurations */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Configurations Disponibles ({configurations.length})
          </Typography>
          
          {configurations.length === 0 ? (
            <Box textAlign="center" py={4}>
              <SettingsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Aucune configuration disponible
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Exportez une configuration pour commencer
              </Typography>
            </Box>
          ) : (
            <List>
              {configurations.map((config, index) => (
                <React.Fragment key={config.filename}>
                  <ListItem>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle1">{config.name}</Typography>
                          <Chip 
                            label={config.format.toUpperCase()} 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                          />
                          <Chip 
                            label={`v${config.version}`} 
                            size="small" 
                            color="secondary" 
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {config.description}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Créé: {formatDate(config.created_at)} | 
                            Modifié: {formatDate(config.updated_at)} | 
                            Taille: {formatFileSize(config.size)}
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton onClick={() => handleDownloadConfiguration(config.filename)}>
                        <DownloadIcon />
                      </IconButton>
                      <IconButton onClick={() => handleDeleteConfiguration(config.filename)}>
                        <DeleteIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < configurations.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Dialog d'export */}
      <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Exporter la Configuration</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary" paragraph>
                Exportez la configuration complète du système incluant :
                règles métier, ontologie, paramètres LLM, et configuration des outils.
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Format</InputLabel>
                <Select
                  value={exportForm.format}
                  onChange={(e) => setExportForm(prev => ({ ...prev, format: e.target.value }))}
                  label="Format"
                >
                  <MenuItem value="json">JSON</MenuItem>
                  <MenuItem value="yaml">YAML</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Nom du fichier (optionnel)"
                value={exportForm.filename}
                onChange={(e) => setExportForm(prev => ({ ...prev, filename: e.target.value }))}
                placeholder="ma_configuration"
                helperText="Laissez vide pour un nom automatique"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialogOpen(false)}>Annuler</Button>
          <Button onClick={handleExportConfiguration} variant="contained">
            Exporter
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog d'import */}
      <Dialog open={importDialogOpen} onClose={() => setImportDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Importer une Configuration</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary" paragraph>
              Importez une configuration depuis un fichier JSON ou YAML.
              La configuration sera appliquée au système.
            </Typography>
            
            <input
              accept=".json,.yaml,.yml"
              style={{ display: 'none' }}
              id="config-file-input"
              type="file"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            />
            <label htmlFor="config-file-input">
              <Button
                variant="outlined"
                component="span"
                startIcon={<UploadIcon />}
                fullWidth
                sx={{ mb: 2 }}
              >
                Sélectionner un fichier
              </Button>
            </label>
            
            {selectedFile && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Fichier sélectionné: {selectedFile.name} ({formatFileSize(selectedFile.size)})
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setImportDialogOpen(false);
            setSelectedFile(null);
          }}>
            Annuler
          </Button>
          <Button 
            onClick={handleImportConfiguration} 
            variant="contained"
            disabled={!selectedFile}
          >
            Importer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ConfigurationManager; 