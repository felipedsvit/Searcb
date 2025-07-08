import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Alert,
  Divider,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Home as HomeIcon,
  BugReport as BugIcon,
} from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // Chamar callback personalizado se fornecido
    this.props.onError?.(error, errorInfo);

    // Em produção, enviar erro para serviço de monitoramento
    if (process.env.NODE_ENV === 'production') {
      // Aqui você integraria com um serviço como Sentry, LogRocket, etc.
      console.error('Production error:', {
        error: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      });
    }
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  handleResetError = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      // Renderizar fallback personalizado se fornecido
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Renderizar tela de erro padrão
      return (
        <Container maxWidth="md" sx={{ py: 4 }}>
          <Paper elevation={3} sx={{ p: 4 }}>
            <Box textAlign="center" mb={3}>
              <BugIcon color="error" sx={{ fontSize: 64, mb: 2 }} />
              <Typography variant="h4" color="error" gutterBottom>
                Oops! Algo deu errado
              </Typography>
              <Typography variant="body1" color="textSecondary" paragraph>
                Ocorreu um erro inesperado na aplicação. Nossa equipe foi notificada 
                e está trabalhando para resolver o problema.
              </Typography>
            </Box>

            <Alert severity="error" sx={{ mb: 3 }}>
              <Typography variant="body2">
                <strong>Erro:</strong> {this.state.error?.message || 'Erro desconhecido'}
              </Typography>
            </Alert>

            <Box display="flex" gap={2} justifyContent="center" mb={3}>
              <Button
                variant="contained"
                startIcon={<RefreshIcon />}
                onClick={this.handleReload}
                color="primary"
              >
                Recarregar Página
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<HomeIcon />}
                onClick={this.handleGoHome}
              >
                Ir para Início
              </Button>
              
              <Button
                variant="text"
                onClick={this.handleResetError}
                color="secondary"
              >
                Tentar Novamente
              </Button>
            </Box>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <>
                <Divider sx={{ my: 3 }} />
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Detalhes do Erro (Desenvolvimento)
                  </Typography>
                  
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    <Typography variant="caption">
                      Estas informações são visíveis apenas em modo de desenvolvimento.
                    </Typography>
                  </Alert>

                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      p: 2, 
                      backgroundColor: 'grey.50',
                      maxHeight: 200,
                      overflow: 'auto',
                    }}
                  >
                    <Typography 
                      variant="body2" 
                      component="pre" 
                      sx={{ 
                        fontFamily: 'monospace',
                        fontSize: '0.75rem',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {this.state.error.stack}
                    </Typography>
                  </Paper>

                  {this.state.errorInfo && (
                    <>
                      <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                        Component Stack:
                      </Typography>
                      <Paper 
                        variant="outlined" 
                        sx={{ 
                          p: 2, 
                          backgroundColor: 'grey.50',
                          maxHeight: 150,
                          overflow: 'auto',
                        }}
                      >
                        <Typography 
                          variant="body2" 
                          component="pre" 
                          sx={{ 
                            fontFamily: 'monospace',
                            fontSize: '0.75rem',
                            whiteSpace: 'pre-wrap',
                          }}
                        >
                          {this.state.errorInfo.componentStack}
                        </Typography>
                      </Paper>
                    </>
                  )}
                </Box>
              </>
            )}
          </Paper>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;