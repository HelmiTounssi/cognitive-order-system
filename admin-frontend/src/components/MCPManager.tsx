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
  Alert,
  CircularProgress,
  Divider,
  MenuItem,
  Select,
  InputLabel,
  FormControl
} from '@mui/material';

// Adresse du serveur MCP (adapter si besoin)
const MCP_SERVER_URL = 'ws://localhost:8002';

interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
}

const MCPManager: React.FC = () => {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [selectedTool, setSelectedTool] = useState<string>('');
  const [toolArgs, setToolArgs] = useState<any>({});
  const [response, setResponse] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Connexion MCP et récupération des outils
  useEffect(() => {
    setStatus('checking');
    setError('');
    setResponse('');
    const socket = new window.WebSocket(MCP_SERVER_URL);
    setWs(socket);
    let isOpen = false;

    socket.onopen = () => {
      isOpen = true;
      setStatus('online');
      // Initialisation
      socket.send(JSON.stringify({
        jsonrpc: '2.0',
        id: 'init',
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          clientInfo: { name: 'AdminFrontend', version: '1.0.0' }
        }
      }));
      // Liste des outils
      setTimeout(() => {
        socket.send(JSON.stringify({
          jsonrpc: '2.0',
          id: 'list',
          method: 'tools/list',
          params: {}
        }));
      }, 200);
    };
    socket.onerror = () => {
      setStatus('offline');
      setError('Impossible de se connecter au serveur MCP.');
    };
    socket.onclose = () => {
      setStatus('offline');
      if (isOpen) setError('Connexion MCP fermée.');
    };
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.result && data.result.tools) {
          setTools(data.result.tools);
        } else if (data.result && data.result.content) {
          setResponse(data.result.content.map((c: any) => c.text).join('\n'));
          setLoading(false);
        } else if (data.error) {
          setError(data.error.message + (data.error.data ? ': ' + data.error.data : ''));
          setLoading(false);
        }
      } catch (e) {
        setError('Erreur de parsing MCP: ' + String(e));
        setLoading(false);
      }
    };
    return () => {
      socket.close();
    };
  }, []);

  // Gestion du formulaire dynamique
  const handleToolChange = (event: any) => {
    setSelectedTool(event.target.value);
    setToolArgs({});
    setResponse('');
    setError('');
  };

  const handleArgChange = (key: string, value: any) => {
    setToolArgs((prev: any) => ({ ...prev, [key]: value }));
  };

  const handleCallTool = () => {
    setLoading(true);
    setResponse('');
    setError('');
    if (!ws || ws.readyState !== 1) {
      setError('WebSocket MCP non connecté.');
      setLoading(false);
      return;
    }
    const tool = tools.find(t => t.name === selectedTool);
    if (!tool) {
      setError('Outil non trouvé.');
      setLoading(false);
      return;
    }
    ws.send(JSON.stringify({
      jsonrpc: '2.0',
      id: 'call_' + selectedTool,
      method: 'tools/call',
      params: {
        name: selectedTool,
        arguments: toolArgs
      }
    }));
  };

  const renderToolForm = () => {
    if (!selectedTool) return null;
    const tool = tools.find(t => t.name === selectedTool);
    if (!tool) return null;
    const schema = tool.inputSchema;
    if (!schema || !schema.properties) return <Typography>Aucun schéma d'entrée.</Typography>;
    return (
      <Box>
        {Object.entries(schema.properties).map(([key, prop]: any) => (
          <Box key={key} mb={2}>
            <TextField
              label={prop.description || key}
              value={toolArgs[key] || ''}
              onChange={e => handleArgChange(key, e.target.value)}
              fullWidth
              type={prop.type === 'number' ? 'number' : 'text'}
            />
          </Box>
        ))}
      </Box>
    );
  };

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6">Gestionnaire MCP (Model Context Protocol)</Typography>
          <Divider sx={{ my: 2 }} />
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Statut du serveur MCP :{' '}
            <b style={{ color: status === 'online' ? 'green' : status === 'offline' ? 'red' : 'orange' }}>
              {status === 'online' ? 'Connecté' : status === 'offline' ? 'Déconnecté' : 'Vérification...'}
            </b>
          </Typography>
          {status === 'checking' && <CircularProgress size={20} sx={{ ml: 2 }} />}
          {status === 'offline' && (
            <Alert severity="error" sx={{ mt: 2 }}>Impossible de se connecter au serveur MCP ({MCP_SERVER_URL})</Alert>
          )}
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1">Outils MCP disponibles</Typography>
          <Divider sx={{ my: 1 }} />
          {tools.length === 0 && <Typography color="text.secondary">Aucun outil MCP détecté.</Typography>}
          <List>
            {tools.map(tool => (
              <ListItem key={tool.name} selected={tool.name === selectedTool} button onClick={() => setSelectedTool(tool.name)}>
                <ListItemText
                  primary={tool.name}
                  secondary={tool.description}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      {selectedTool && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1">Tester l'outil : <b>{selectedTool}</b></Typography>
            <Divider sx={{ my: 1 }} />
            {renderToolForm()}
            <Button
              variant="contained"
              color="primary"
              onClick={handleCallTool}
              disabled={loading}
              sx={{ mt: 2 }}
            >
              Appeler l'outil
            </Button>
            {loading && <CircularProgress size={20} sx={{ ml: 2 }} />}
            {response && (
              <Alert severity="success" sx={{ mt: 2, whiteSpace: 'pre-line' }}>{response}</Alert>
            )}
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default MCPManager; 