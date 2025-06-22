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
      console.error('Erreur lors du chargement des suggestions');
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
          setSuggestions([]);
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
        const blob = new Blob([JSON.stringify(data.conversation, null, 2)], {
          type: 'application/json'
        });
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
      healthcare: '#e3f2fd',
      ecommerce: '#f3e5f5',
      restaurant: '#e8f5e8',
      generic: '#f5f5f5'
    };
    return colors[domain] || colors.generic;
  };

  const getDomainLabel = (domain: string) => {
    const labels: { [key: string]: string } = {
      healthcare: 'Santé',
      ecommerce: 'E-commerce',
      restaurant: 'Restaurant',
      generic: 'Générique'
    };
    return labels[domain] || 'Générique';
  };

  const checkRAGStatus = async () => {
    try {
      setRagStatus('checking');
      const response = await fetch(`${API_BASE}/rag/status`);
      const data = await response.json();
      if (data.success && data.status === 'online') {
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
      case 'checking': return 'warning';
      default: return 'default';
    }
  };

  const getStatusText = () => {
    switch (ragStatus) {
      case 'online': return 'RAG Online';
      case 'offline': return 'RAG Offline';
      case 'checking': return 'Vérification...';
      default: return 'Inconnu';
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar des conversations */}
      <Drawer
        variant="permanent"
        sx={{
          width: 320,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 320,
            boxSizing: 'border-box',
          },
        }}
      >
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" gutterBottom>
            Conversations RAG
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={createNewConversation}
            fullWidth
            sx={{ mb: 2 }}
          >
            Nouvelle conversation
          </Button>
        </Box>

        <List sx={{ flex: 1, overflow: 'auto' }}>
          {conversations.map((conversation) => (
            <ListItem
              key={conversation.id}
              button
              selected={currentConversation?.id === conversation.id}
              onClick={() => loadConversation(conversation.id)}
              sx={{ flexDirection: 'column', alignItems: 'flex-start' }}
            >
              <Box sx={{ display: 'flex', width: '100%', justifyContent: 'space-between' }}>
                <Typography variant="subtitle2" noWrap sx={{ maxWidth: '200px' }}>
                  {conversation.title}
                </Typography>
                <Box>
                  <Tooltip title="Analytics">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        loadAnalytics(conversation.id);
                      }}
                    >
                      <AnalyticsIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Exporter">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        exportConversation(conversation.id);
                      }}
                    >
                      <DownloadIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Supprimer">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteConversation(conversation.id);
                      }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                <Chip
                  label={getDomainLabel(conversation.domain)}
                  size="small"
                  sx={{ backgroundColor: getDomainColor(conversation.domain) }}
                />
                <Typography variant="caption" color="text.secondary">
                  {conversation.message_count} messages
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                {new Date(conversation.updated_at).toLocaleDateString()}
              </Typography>
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Zone de chat principale */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <Paper sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <ChatIcon />
              <Typography variant="h6">
                {currentConversation?.title || 'Assistant RAG'}
              </Typography>
              {currentConversation && (
                <Chip
                  label={getDomainLabel(currentConversation.domain)}
                  sx={{ backgroundColor: getDomainColor(currentConversation.domain) }}
                />
              )}
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                label={getStatusText()}
                color={getStatusColor() as any}
                size="small"
                icon={ragStatus === 'checking' ? <CircularProgress size={16} /> : undefined}
              />
              <Tooltip title="Vérifier le statut RAG">
                <IconButton
                  size="small"
                  onClick={checkRAGStatus}
                  disabled={ragStatus === 'checking'}
                >
                  <CloseIcon sx={{ transform: 'rotate(45deg)' }} />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Paper>

        {/* Messages */}
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {messages.length === 0 ? (
            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <ChatIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Commencez une nouvelle conversation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Posez vos questions sur les workflows, patterns et règles métier
              </Typography>
            </Box>
          ) : (
            <>
              {messages.map((message) => (
                <Box
                  key={message.id}
                  sx={{
                    display: 'flex',
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    mb: 2
                  }}
                >
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      backgroundColor: message.sender === 'user' ? 'primary.main' : 'grey.100',
                      color: message.sender === 'user' ? 'white' : 'text.primary'
                    }}
                  >
                    <Typography variant="body1">{message.content}</Typography>
                    {message.metadata && (
                      <Box sx={{ mt: 1 }}>
                        {message.metadata.confidence && (
                          <Chip
                            label={`Confiance: ${(message.metadata.confidence * 100).toFixed(1)}%`}
                            size="small"
                            color={message.metadata.confidence > 0.7 ? 'success' : 'warning'}
                          />
                        )}
                        {message.metadata.suggested_actions && message.metadata.suggested_actions.length > 0 && (
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              Actions suggérées:
                            </Typography>
                            {message.metadata.suggested_actions.map((action: string, index: number) => (
                              <Chip
                                key={index}
                                label={action}
                                size="small"
                                variant="outlined"
                                sx={{ mr: 0.5, mt: 0.5 }}
                              />
                            ))}
                          </Box>
                        )}
                      </Box>
                    )}
                    <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </Typography>
                  </Paper>
                </Box>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </Box>

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="subtitle2" gutterBottom>
              <LightbulbIcon sx={{ mr: 1, fontSize: 16 }} />
              Suggestions
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {suggestions.map((suggestion, index) => (
                <Chip
                  key={index}
                  label={suggestion}
                  clickable
                  onClick={() => setInputMessage(suggestion)}
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Zone de saisie */}
        <Paper sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Posez votre question..."
              disabled={isLoading}
            />
            <Button
              variant="contained"
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              sx={{ minWidth: 'auto', px: 2 }}
            >
              {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
            </Button>
          </Box>
        </Paper>
      </Box>

      {/* Dialog Analytics */}
      <Dialog open={analyticsOpen} onClose={() => setAnalyticsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Analytics de la conversation
          <IconButton
            onClick={() => setAnalyticsOpen(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {analytics && (
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Messages</Typography>
                    <Typography variant="h4">{analytics.total_messages}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total des échanges
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Confiance</Typography>
                    <Typography variant="h4">
                      {(analytics.average_confidence * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Moyenne des réponses
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Sources</Typography>
                    <Typography variant="h4">{analytics.sources_used?.length || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Types de sources utilisées
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Actions</Typography>
                    <Typography variant="h4">{analytics.suggested_actions_count || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Actions suggérées
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Sujets discutés</Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                      {analytics.topics?.map((topic: string, index: number) => (
                        <Chip key={index} label={topic} size="small" />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default RAGChatInterface; 