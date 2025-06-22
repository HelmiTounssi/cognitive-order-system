import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  IconButton,
  Drawer,
  Divider,
  Card,
  CardContent,
  Grid,
  Tooltip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Send as SendIcon,
  Chat as ChatIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Lightbulb as LightbulbIcon,
  Analytics as AnalyticsIcon,
  Add as AddIcon,
  Close as CloseIcon
} from '@mui/icons-material';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: string;
  metadata?: any;
  rag_context?: any;
}

interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  domain: string;
  message_count: number;
  summary: any;
}

interface RAGResponse {
  id: string;
  content: string;
  timestamp: string;
  metadata: any;
  rag_context: any;
}

const RAGChatInterface: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [analyticsOpen, setAnalyticsOpen] = useState(false);
  const [analytics, setAnalytics] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [ragStatus, setRagStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const API_BASE = 'http://localhost:5001/api';

  useEffect(() => {
    loadConversations();
    checkRAGStatus();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      const response = await fetch(`${API_BASE}/rag/conversations`);
      const data = await response.json();
      if (data.success) {
        setConversations(data.conversations);
      }
    } catch (error) {
      setError('Erreur lors du chargement des conversations');
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await fetch(`${API_BASE}/rag/conversations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initial_query: null })
      });
      const data = await response.json();
      if (data.success) {
        await loadConversations();
        await loadConversation(data.conversation_id);
      }
    } catch (error) {
      setError('Erreur lors de la création de conversation');
    }
  };

  const loadConversation = async (conversationId: string) => {
    try {
      const response = await fetch(`${API_BASE}/rag/conversations/${conversationId}`);
      const data = await response.json();
      if (data.success) {
        setCurrentConversation({
          id: data.conversation.id,
          title: data.conversation.title,
          created_at: data.conversation.created_at,
          updated_at: data.conversation.updated_at,
          domain: data.conversation.domain,
          message_count: data.conversation.messages.length,
          summary: data.conversation.summary
        });
        setMessages(data.conversation.messages);
        await loadSuggestions(conversationId);
      }
    } catch (error) {
      setError('Erreur lors du chargement de la conversation');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/rag/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          conversation_id: currentConversation?.id
        })
      });

      const data = await response.json();
      if (data.success) {
        const assistantMessage: Message = {
          id: data.response.id,
          content: data.response.content,
          sender: 'assistant',
          timestamp: data.response.timestamp,
          metadata: data.response.metadata,
          rag_context: data.response.rag_context
        };

        setMessages(prev => [...prev, assistantMessage]);
        
        // Mettre à jour la conversation courante
        if (data.conversation_id) {
          await loadConversations();
          await loadConversation(data.conversation_id);
        }
      } else {
        setError(data.error || 'Erreur lors de l\'envoi du message');
      }
    } catch (error) {
      setError('Erreur de connexion');
    } finally {
      setIsLoading(false);
    }
  };

  const loadSuggestions = async (conversationId: string) => {
    try {
      const response = await fetch(`${API_BASE}/rag/conversations/${conversationId}/suggestions`);
      const data = await response.json();
      if (data.success) {
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des suggestions:', error);
    }
  };

  const loadAnalytics = async (conversationId: string) => {
    try {
      const response = await fetch(`${API_BASE}/rag/conversations/${conversationId}/analytics`);
      const data = await response.json();
      if (data.success) {
        setAnalytics(data.analytics);
        setAnalyticsOpen(true);
      }
    } catch (error) {
      setError('Erreur lors du chargement des analytics');
    }
  };

  const deleteConversation = async (conversationId: string) => {
    try {
      const response = await fetch(`${API_BASE}/rag/conversations/${conversationId}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        await loadConversations();
        if (currentConversation?.id === conversationId) {
          setCurrentConversation(null);
          setMessages([]);
        }
      }
    } catch (error) {
      setError('Erreur lors de la suppression');
    }
  };

  const exportConversation = async (conversationId: string) => {
    try {
      const response = await fetch(`${API_BASE}/rag/conversations/${conversationId}/export`);
      const data = await response.json();
      if (data.success) {
        const blob = new Blob([JSON.stringify(data.conversation, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation_${conversationId}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      setError('Erreur lors de l\'export');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const getDomainColor = (domain: string) => {
    const colors: { [key: string]: string } = {
      'ecommerce': '#4caf50',
      'healthcare': '#2196f3',
      'finance': '#ff9800',
      'education': '#9c27b0',
      'default': '#757575'
    };
    return colors[domain] || colors.default;
  };

  const getDomainLabel = (domain: string) => {
    const labels: { [key: string]: string } = {
      'ecommerce': 'E-commerce',
      'healthcare': 'Santé',
      'finance': 'Finance',
      'education': 'Éducation',
      'default': 'Général'
    };
    return labels[domain] || labels.default;
  };

  const checkRAGStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/rag/status`);
      const data = await response.json();
      if (data.success) {
        setRagStatus('online');
      } else {
        setRagStatus('offline');
      }
    } catch (error) {
      setRagStatus('offline');
    }
  };

  const getStatusColor = () => {
    switch (ragStatus) {
      case 'online': return 'success';
      case 'offline': return 'error';
      default: return 'warning';
    }
  };

  const getStatusText = () => {
    switch (ragStatus) {
      case 'online': return 'Connecté';
      case 'offline': return 'Déconnecté';
      default: return 'Vérification...';
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header avec statut */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ py: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">💬 Interface RAG - Assistant IA</Typography>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Chip
                label={getStatusText()}
                color={getStatusColor() as any}
                size="small"
                variant={ragStatus === 'online' ? 'filled' : 'outlined'}
              />
              <Button
                variant="outlined"
                size="small"
                onClick={() => setDrawerOpen(true)}
                startIcon={<ChatIcon />}
              >
                Conversations ({conversations.length})
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Messages d'erreur */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Interface principale */}
      <Box sx={{ flexGrow: 1, display: 'flex', gap: 2, minHeight: 0 }}>
        {/* Zone de chat */}
        <Card sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 0 }}>
            {/* En-tête de conversation */}
            {currentConversation && (
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: 'grey.50' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h6">{currentConversation.title}</Typography>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Chip
                        label={getDomainLabel(currentConversation.domain)}
                        size="small"
                        sx={{ bgcolor: getDomainColor(currentConversation.domain), color: 'white' }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {currentConversation.message_count} messages
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton size="small" onClick={() => loadAnalytics(currentConversation.id)}>
                      <AnalyticsIcon />
                    </IconButton>
                    <IconButton size="small" onClick={() => exportConversation(currentConversation.id)}>
                      <DownloadIcon />
                    </IconButton>
                    <IconButton size="small" onClick={() => deleteConversation(currentConversation.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
              </Box>
            )}

            {/* Messages */}
            <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2, minHeight: 0 }}>
              {messages.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    {currentConversation ? 'Aucun message dans cette conversation' : 'Aucune conversation sélectionnée'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {currentConversation ? 'Commencez à discuter avec l\'assistant IA' : 'Sélectionnez une conversation ou créez-en une nouvelle'}
                  </Typography>
                </Box>
              ) : (
                <List sx={{ p: 0 }}>
                  {messages.map((message) => (
                    <ListItem key={message.id} sx={{ flexDirection: 'column', alignItems: 'flex-start', p: 0, mb: 2 }}>
                      <Box sx={{ 
                        display: 'flex', 
                        gap: 1, 
                        width: '100%',
                        justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start'
                      }}>
                        {message.sender === 'assistant' && (
                          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                            <ChatIcon />
                          </Avatar>
                        )}
                        <Paper sx={{ 
                          p: 2, 
                          maxWidth: '70%',
                          bgcolor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                          color: message.sender === 'user' ? 'white' : 'text.primary'
                        }}>
                          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                            {message.content}
                          </Typography>
                          {message.rag_context && (
                            <Box sx={{ mt: 1, pt: 1, borderTop: 1, borderColor: 'divider' }}>
                              <Typography variant="caption" color="text.secondary">
                                Sources: {message.rag_context.sources?.length || 0} documents
                              </Typography>
                            </Box>
                          )}
                        </Paper>
                        {message.sender === 'user' && (
                          <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                            👤
                          </Avatar>
                        )}
                      </Box>
                    </ListItem>
                  ))}
                  {isLoading && (
                    <ListItem sx={{ justifyContent: 'flex-start', p: 0, mb: 2 }}>
                      <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32, mr: 1 }}>
                        <ChatIcon />
                      </Avatar>
                      <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
                        <CircularProgress size={20} />
                      </Paper>
                    </ListItem>
                  )}
                  <div ref={messagesEndRef} />
                </List>
              )}
            </Box>

            {/* Suggestions */}
            {suggestions.length > 0 && (
              <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'grey.50' }}>
                <Typography variant="subtitle2" gutterBottom>
                  💡 Suggestions
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {suggestions.map((suggestion, index) => (
                    <Chip
                      key={index}
                      label={suggestion}
                      size="small"
                      onClick={() => setInputMessage(suggestion)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </Box>
            )}

            {/* Zone de saisie */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={4}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Posez votre question à l'assistant IA..."
                  disabled={isLoading}
                  size="small"
                />
                <Button
                  variant="contained"
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || isLoading}
                  sx={{ minWidth: 'auto', px: 2 }}
                >
                  <SendIcon />
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Drawer des conversations */}
      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{ '& .MuiDrawer-paper': { width: 350 } }}
      >
        <Box sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Conversations</Typography>
            <IconButton onClick={() => setDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
          
          <Button
            variant="contained"
            fullWidth
            onClick={createNewConversation}
            startIcon={<AddIcon />}
            sx={{ mb: 2 }}
          >
            Nouvelle conversation
          </Button>

          <List>
            {conversations.map((conversation) => (
              <ListItem
                key={conversation.id}
                button
                selected={currentConversation?.id === conversation.id}
                onClick={() => {
                  loadConversation(conversation.id);
                  setDrawerOpen(false);
                }}
                sx={{ flexDirection: 'column', alignItems: 'flex-start' }}
              >
                <ListItemText
                  primary={conversation.title}
                  secondary={
                    <Box>
                      <Chip
                        label={getDomainLabel(conversation.domain)}
                        size="small"
                        sx={{ bgcolor: getDomainColor(conversation.domain), color: 'white', mr: 1 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        {conversation.message_count} messages • {new Date(conversation.updated_at).toLocaleDateString()}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Dialog Analytics */}
      <Dialog open={analyticsOpen} onClose={() => setAnalyticsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Analytics de la conversation</DialogTitle>
        <DialogContent>
          {analytics && (
            <Box>
              <Typography variant="h6" gutterBottom>Statistiques</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h4">{analytics.total_messages}</Typography>
                    <Typography variant="body2">Messages totaux</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <Typography variant="h4">{analytics.avg_response_time}s</Typography>
                    <Typography variant="body2">Temps de réponse moyen</Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalyticsOpen(false)}>Fermer</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RAGChatInterface; 