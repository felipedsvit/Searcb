import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuthStore, usePermissions } from '../../stores/authStore';
import { ROUTES } from '../../utils/constants';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles,
  fallback,
  redirectTo = ROUTES.LOGIN,
}) => {
  const location = useLocation();
  const { isAuthenticated, isLoading } = useAuthStore();
  const { canAccess } = usePermissions();

  // Mostrar loading enquanto verifica autenticação
  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  // Se não estiver autenticado, redirecionar para login
  if (!isAuthenticated) {
    return (
      <Navigate
        to={redirectTo}
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // Verificar permissões de acesso
  if (!canAccess(requiredRoles)) {
    if (fallback) {
      return <>{fallback}</>;
    }

    // Redirecionar para página de acesso negado ou dashboard
    return (
      <Navigate
        to={ROUTES.DASHBOARD}
        replace
      />
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;