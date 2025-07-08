import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useLocation, Navigate } from 'react-router-dom';
import {
  Box,
  Container,
  TextField,
  Button,
  Typography,
  Checkbox,
  FormControlLabel,
  Link,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
  Card,
  CardContent,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Login as LoginIcon,
} from '@mui/icons-material';
import { loginSchema } from '../../utils/validators';
import { useAuth } from '../../hooks/useAuth';
import { LoadingScreen } from '../../components/common/LoadingScreen';
import type { LoginCredentials } from '../../types/api';
import { ROUTES } from '../../utils/constants';

export const Login: React.FC = () => {
  const location = useLocation();
  const { login, isAuthenticated, isLoading, error, clearError } = useAuth();
  
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
  } = useForm<LoginCredentials>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const from = (location.state as any)?.from || ROUTES.DASHBOARD;

  // Redirecionar se já estiver autenticado
  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  // Limpar erro quando os campos mudarem
  useEffect(() => {
    const subscription = watch(() => {
      if (error) {
        clearError();
      }
    });
    return () => subscription.unsubscribe();
  }, [watch, error, clearError]);

  const onSubmit = async (data: LoginCredentials) => {
    try {
      await login(data, from);
      
      // Salvar preferência de "lembrar-me"
      if (rememberMe) {
        localStorage.setItem('remember_email', data.email);
      } else {
        localStorage.removeItem('remember_email');
      }
    } catch (error) {
      // Erro já tratado no hook useAuth
    }
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Carregar email salvo se "lembrar-me" estava ativado
  useEffect(() => {
    const savedEmail = localStorage.getItem('remember_email');
    if (savedEmail) {
      setRememberMe(true);
    }
  }, []);

  if (isLoading) {
    return <LoadingScreen loading={{ isLoading: true, message: 'Verificando autenticação...' }} />;
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        p: 2,
      }}
    >
      <Container maxWidth="sm">
        <Card
          elevation={24}
          sx={{
            borderRadius: 3,
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
              color: 'white',
              py: 4,
              textAlign: 'center',
            }}
          >
            <Typography variant="h3" component="h1" fontWeight="bold" gutterBottom>
              SEARCB
            </Typography>
            <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
              Sistema de Acompanhamento de Registros de Contratações Brasileiras
            </Typography>
          </Box>

          <CardContent sx={{ p: 4 }}>
            <Box sx={{ mb: 3, textAlign: 'center' }}>
              <Typography variant="h5" component="h2" gutterBottom>
                Entrar no Sistema
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Digite suas credenciais para acessar o sistema
              </Typography>
            </Box>

            {error && (
              <Alert 
                severity="error" 
                sx={{ mb: 3 }}
                onClose={clearError}
              >
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit(onSubmit)} noValidate>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="E-mail"
                    type="email"
                    autoComplete="email"
                    autoFocus
                    error={!!errors.email}
                    helperText={errors.email?.message}
                    sx={{ mb: 2 }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Email color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                )}
              />

              <Controller
                name="password"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="Senha"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    error={!!errors.password}
                    helperText={errors.password?.message}
                    sx={{ mb: 2 }}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Lock color="action" />
                        </InputAdornment>
                      ),
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={handleTogglePasswordVisibility}
                            edge="end"
                            size="small"
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />
                )}
              />

              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 3,
                }}
              >
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Lembrar-me"
                />

                <Link
                  href="#"
                  variant="body2"
                  sx={{ textDecoration: 'none' }}
                  onClick={(e) => {
                    e.preventDefault();
                    // TODO: Implementar recuperação de senha
                  }}
                >
                  Esqueceu a senha?
                </Link>
              </Box>

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={isSubmitting}
                startIcon={<LoginIcon />}
                sx={{
                  py: 1.5,
                  mb: 3,
                  background: 'linear-gradient(45deg, #1976d2 30%, #42a5f5 90%)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #1565c0 30%, #1976d2 90%)',
                  },
                }}
              >
                {isSubmitting ? 'Entrando...' : 'Entrar'}
              </Button>

              <Divider sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary">
                  Precisa de ajuda?
                </Typography>
              </Divider>

              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="textSecondary" paragraph>
                  Entre em contato com o administrador do sistema para:
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  • Criação de nova conta
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  • Recuperação de senha
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  • Problemas técnicos
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>

        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="white" sx={{ opacity: 0.8 }}>
            © 2024 SEARCB. Todos os direitos reservados.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
};

export default Login;