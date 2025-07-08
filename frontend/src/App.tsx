import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { theme } from './styles/theme';
import { useAuthStore } from './stores/authStore';
import { ROUTES } from './utils/constants';

// Layout Components
import MainLayout from './components/layout/MainLayout';
import ErrorBoundary from './components/common/ErrorBoundary';
import LoadingScreen from './components/common/LoadingScreen';
import ProtectedRoute from './components/common/ProtectedRoute';
import ToastContainer from './components/ui/ToastContainer';
import ModalContainer from './components/ui/ModalContainer';

// Pages
import Login from './pages/auth/Login';

// Lazy load pages for better performance
const Dashboard = React.lazy(() => import('./pages/dashboard/Dashboard'));
const PCAs = React.lazy(() => import('./pages/entities/PCAs'));
const Contratos = React.lazy(() => import('./pages/entities/Contratos'));
const Contratacoes = React.lazy(() => import('./pages/entities/Contratacoes'));
const Atas = React.lazy(() => import('./pages/entities/Atas'));
const Usuarios = React.lazy(() => import('./pages/entities/Usuarios'));
const Relatorios = React.lazy(() => import('./pages/dashboard/Relatorios'));
const Configuracoes = React.lazy(() => import('./pages/dashboard/Configuracoes'));
const Perfil = React.lazy(() => import('./pages/dashboard/Perfil'));

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    },
    mutations: {
      retry: 1,
    },
  },
});

const App: React.FC = () => {
  const { checkAuth, isLoading } = useAuthStore();

  // Check authentication status on app load
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LoadingScreen 
          loading={{ 
            isLoading: true, 
            message: 'Inicializando aplicação...' 
          }} 
          fullScreen 
        />
      </ThemeProvider>
    );
  }

  return (
    <ErrorBoundary>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <QueryClientProvider client={queryClient}>
          <Router>
            <Routes>
              {/* Public Routes */}
              <Route path={ROUTES.LOGIN} element={<Login />} />
              
              {/* Protected Routes */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <MainLayout />
                  </ProtectedRoute>
                }
              >
                {/* Dashboard */}
                <Route
                  index
                  element={<Navigate to={ROUTES.DASHBOARD} replace />}
                />
                <Route
                  path={ROUTES.DASHBOARD.substring(1)}
                  element={
                    <React.Suspense fallback={
                      <LoadingScreen 
                        loading={{ isLoading: true, message: 'Carregando dashboard...' }} 
                        fullScreen={false}
                      />
                    }>
                      <Dashboard />
                    </React.Suspense>
                  }
                />

                {/* Entities */}
                <Route
                  path={ROUTES.PCAS.substring(1)}
                  element={
                    <React.Suspense fallback={
                      <LoadingScreen 
                        loading={{ isLoading: true, message: 'Carregando PCAs...' }} 
                        fullScreen={false}
                      />
                    }>
                      <PCAs />
                    </React.Suspense>
                  }
                />
                <Route
                  path={ROUTES.CONTRATOS.substring(1)}
                  element={
                    <React.Suspense fallback={
                      <LoadingScreen 
                        loading={{ isLoading: true, message: 'Carregando contratos...' }} 
                        fullScreen={false}
                      />
                    }>
                      <Contratos />
                    </React.Suspense>
                  }
                />
                <Route
                  path={ROUTES.CONTRATACOES.substring(1)}
                  element={
                    <React.Suspense fallback={
                      <LoadingScreen 
                        loading={{ isLoading: true, message: 'Carregando contratações...' }} 
                        fullScreen={false}
                      />
                    }>
                      <Contratacoes />
                    </React.Suspense>
                  }
                />
                <Route
                  path={ROUTES.ATAS.substring(1)}
                  element={
                    <React.Suspense fallback={
                      <LoadingScreen 
                        loading={{ isLoading: true, message: 'Carregando atas...' }} 
                        fullScreen={false}
                      />
                    }>
                      <Atas />
                    </React.Suspense>
                  }
                />

                {/* Admin Routes */}
                <Route
                  path={ROUTES.USUARIOS.substring(1)}
                  element={
                    <ProtectedRoute requiredRoles={['admin']}>
                      <React.Suspense fallback={
                        <LoadingScreen 
                          loading={{ isLoading: true, message: 'Carregando usuários...' }} 
                          fullScreen={false}
                        />
                      }>
                        <Usuarios />
                      </React.Suspense>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.RELATORIOS.substring(1)}
                  element={
                    <ProtectedRoute requiredRoles={['admin', 'gestor']}>
                      <React.Suspense fallback={
                        <LoadingScreen 
                          loading={{ isLoading: true, message: 'Carregando relatórios...' }} 
                          fullScreen={false}
                        />
                      }>
                        <Relatorios />
                      </React.Suspense>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path={ROUTES.CONFIGURACOES.substring(1)}
                  element={
                    <ProtectedRoute requiredRoles={['admin']}>
                      <React.Suspense fallback={
                        <LoadingScreen 
                          loading={{ isLoading: true, message: 'Carregando configurações...' }} 
                          fullScreen={false}
                        />
                      }>
                        <Configuracoes />
                      </React.Suspense>
                    </ProtectedRoute>
                  }
                />

                {/* Profile */}
                <Route
                  path={ROUTES.PERFIL.substring(1)}
                  element={
                    <React.Suspense fallback={
                      <LoadingScreen 
                        loading={{ isLoading: true, message: 'Carregando perfil...' }} 
                        fullScreen={false}
                      />
                    }>
                      <Perfil />
                    </React.Suspense>
                  }
                />
              </Route>

              {/* 404 Route */}
              <Route 
                path="*" 
                element={<Navigate to={ROUTES.DASHBOARD} replace />} 
              />
            </Routes>
          </Router>

          {/* Global UI Components */}
          <ToastContainer />
          <ModalContainer />

          {/* Development Tools */}
          {process.env.NODE_ENV === 'development' && (
            <ReactQueryDevtools initialIsOpen={false} />
          )}
        </QueryClientProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default App;
