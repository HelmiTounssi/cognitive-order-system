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
  Chip,
  Alert,
  CircularProgress,
  Divider,
  Grid
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Storage as StorageIcon,
  Upload as UploadIcon,
  Download as DownloadIcon
} from '@mui/icons-material';

interface Entity {
  name: string;
  properties: string[];
  description?: string;
  uri?: string;
}

interface OntologyManagerProps {
  apiBaseUrl?: string;
}

const OntologyManager: React.FC<OntologyManagerProps> = ({ 
  apiBaseUrl = 'http://localhost:5001' 
}) => {
  const [entities, setEntities] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Dialog states
  const [entityDialogOpen, setEntityDialogOpen] = useState(false);
  const [editingEntity, setEditingEntity] = useState<Entity | null>(null);
  
  // Form states
  const [entityForm, setEntityForm] = useState({
    name: '',
    description: '',
    properties: [] as string[],
    newProperty: ''
  });

  useEffect(() => {
    loadEntities();
  }, []);

  const loadEntities = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiBaseUrl}/api/ontology/entities`);
      if (response.ok) {
        const data = await response.json();
        setEntities(data.entities || []);
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

  const handleCreateEntity = async () => {
    if (!entityForm.name.trim()) {
      setError('Le nom de l\'entité est requis');
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/api/ontology/entities`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: entityForm.name,
          description: entityForm.description,
          properties: entityForm.properties
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Entité "${entityForm.name}" créée avec succès!`);
        setEntityDialogOpen(false);
        resetForm();
        loadEntities(); // Recharger la liste
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de la création');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleUpdateEntity = async () => {
    if (!editingEntity || !entityForm.name.trim()) {
      setError('Le nom de l\'entité est requis');
      return;
    }

    try {
      const response = await fetch(`${apiBaseUrl}/api/ontology/entities/${editingEntity.name}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: entityForm.name,
          description: entityForm.description,
          properties: entityForm.properties
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Entité "${entityForm.name}" mise à jour avec succès!`);
        setEntityDialogOpen(false);
        setEditingEntity(null);
        resetForm();
        loadEntities(); // Recharger la liste
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de la mise à jour');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleDeleteEntity = async (entityName: string) => {
    if (!window.confirm(`Supprimer l'entité "${entityName}" ?`)) return;

    try {
      const response = await fetch(`${apiBaseUrl}/api/ontology/entities/${entityName}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        alert(`Entité "${entityName}" supprimée avec succès!`);
        loadEntities(); // Recharger la liste
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de la suppression');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
  };

  const handleEditEntity = (entity: Entity) => {
    setEditingEntity(entity);
    setEntityForm({
      name: entity.name,
      description: entity.description || '',
      properties: [...entity.properties],
      newProperty: ''
    });
    setEntityDialogOpen(true);
  };

  const handleAddProperty = () => {
    if (entityForm.newProperty.trim() && !entityForm.properties.includes(entityForm.newProperty.trim())) {
      setEntityForm(prev => ({
        ...prev,
        properties: [...prev.properties, entityForm.newProperty.trim()],
        newProperty: ''
      }));
    }
  };

  const handleRemoveProperty = (property: string) => {
    setEntityForm(prev => ({
      ...prev,
      properties: prev.properties.filter(p => p !== property)
    }));
  };

  const resetForm = () => {
    setEntityForm({
      name: '',
      description: '',
      properties: [],
      newProperty: ''
    });
    setEditingEntity(null);
  };

  const handleExportOntology = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/api/ontology/export`);
      if (response.ok) {
        const data = await response.json();
        const blob = new Blob([JSON.stringify(data.ontology, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ontology.json';
        a.click();
        URL.revokeObjectURL(url);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Erreur lors de l\'export');
      }
    } catch (err) {
      setError('Erreur de connexion');
    }
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
            <Typography variant="h6">Gestionnaire d'Ontologie</Typography>
            <Box>
              <Button
                startIcon={<AddIcon />}
                variant="contained"
                onClick={() => {
                  resetForm();
                  setEntityDialogOpen(true);
                }}
                sx={{ mr: 1 }}
              >
                Ajouter une Entité
              </Button>
              <Button
                startIcon={<DownloadIcon />}
                variant="outlined"
                onClick={handleExportOntology}
                sx={{ mr: 1 }}
              >
                Exporter
              </Button>
              <Button
                startIcon={<UploadIcon />}
                variant="outlined"
              >
                Importer
              </Button>
            </Box>
          </Box>

          <Typography variant="body2" color="text.secondary">
            Gérez les entités de l'ontologie RDF et leurs propriétés
          </Typography>
        </CardContent>
      </Card>

      {!loading && entities.length === 0 && (
        <Alert severity="info" sx={{ mt: 2 }}>
          Aucune entité d'ontologie trouvée. Importez une configuration ou créez une entité pour commencer.
        </Alert>
      )}

      {/* Liste des entités */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Entités de l'Ontologie ({entities.length})
          </Typography>
          
          {entities.length === 0 ? (
            <Box textAlign="center" py={4}>
              <StorageIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Aucune entité définie
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Créez votre première entité pour commencer
              </Typography>
            </Box>
          ) : (
            (() => {
              try {
                return (
                  <List>
                    {entities.map((entity, idx) => (
                      <ListItem key={entity.name || idx}>
                        <ListItemText
                          primary={entity.name}
                          secondary={
                            <>
                              {entity.description && <span>{entity.description}<br/></span>}
                              Propriétés : {Array.isArray(entity.properties) ? entity.properties.join(', ') : 'Aucune'}
                            </>
                          }
                        />
                        <ListItemSecondaryAction>
                          <IconButton onClick={() => handleEditEntity(entity)}>
                            <EditIcon />
                          </IconButton>
                          <IconButton onClick={() => handleDeleteEntity(entity.name)}>
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                );
              } catch (e) {
                return <Alert severity="error">Erreur d'affichage des entités : {String(e)}</Alert>;
              }
            })()
          )}
        </CardContent>
      </Card>

      {/* Dialog de création/édition d'entité */}
      <Dialog open={entityDialogOpen} onClose={() => setEntityDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingEntity ? 'Modifier l\'Entité' : 'Créer une Nouvelle Entité'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Nom de l'entité"
                value={entityForm.name}
                onChange={(e) => setEntityForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Ex: Product, Order, Customer"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={entityForm.description}
                onChange={(e) => setEntityForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Description de l'entité"
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Propriétés
              </Typography>
              <Box display="flex" gap={1} mb={2}>
                <TextField
                  label="Nouvelle propriété"
                  value={entityForm.newProperty}
                  onChange={(e) => setEntityForm(prev => ({ ...prev, newProperty: e.target.value }))}
                  placeholder="Ex: name, price, quantity"
                  onKeyPress={(e) => e.key === 'Enter' && handleAddProperty()}
                  sx={{ flexGrow: 1 }}
                />
                <Button 
                  variant="outlined" 
                  onClick={handleAddProperty}
                  disabled={!entityForm.newProperty.trim()}
                >
                  Ajouter
                </Button>
              </Box>
              {entityForm.properties.length > 0 && (
                <Box>
                  {entityForm.properties.map((prop, idx) => (
                    <Chip 
                      key={idx} 
                      label={prop} 
                      onDelete={() => handleRemoveProperty(prop)}
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              )}
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setEntityDialogOpen(false);
            resetForm();
          }}>
            Annuler
          </Button>
          <Button 
            onClick={editingEntity ? handleUpdateEntity : handleCreateEntity}
            variant="contained"
            disabled={!entityForm.name.trim()}
          >
            {editingEntity ? 'Mettre à jour' : 'Créer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OntologyManager; 