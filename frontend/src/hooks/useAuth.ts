import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useToast } from '../stores/uiStore';
import type { LoginCredentials } from '../types/api';
import { ROUTES } from '../utils/constants';

export const useAuth = () => {
  const navigate = useNavigate();
  const toast = useToast();
  
  const {
    user,
    token,
    isLoading,
    isAuthenticated,
    error,
    login: loginAction,
    logout: logoutAction,
    refreshToken,
    updateUser,
    clearError,
    checkAuth,
  } = useAuthStore();

  const login = useCallback(
    async (credentials: LoginCredentials, redirectTo?: string) => {
      try {
        await loginAction(credentials);
        
        toast.success(
          'Login realizado com sucesso',
          `Bem-vindo(a), ${credentials.email}!`
        );
        
        // Redirecionar para a página solicitada ou dashboard
        const destination = redirectTo || ROUTES.DASHBOARD;
        navigate(destination, { replace: true });
      } catch (error: any) {
        toast.error(
          'Erro no login',
          error.message || 'Credenciais inválidas'
        );
        throw error;
      }
    },
    [loginAction, navigate, toast]
  );

  const logout = useCallback(() => {
    logoutAction();
    toast.info('Logout realizado', 'Você foi desconectado do sistema');
  }, [logoutAction, toast]);

  const handleTokenRefresh = useCallback(async () => {
    try {
      await refreshToken();
    } catch (error: any) {
      toast.error(
        'Sessão expirada',
        'Sua sessão expirou. Faça login novamente.'
      );
      logout();
    }
  }, [refreshToken, logout, toast]);

  const updateProfile = useCallback(
    async (userData: Parameters<typeof updateUser>[0]) => {
      try {
        updateUser(userData);
        toast.success(
          'Perfil atualizado',
          'Suas informações foram atualizadas com sucesso'
        );
      } catch (error: any) {
        toast.error(
          'Erro ao atualizar perfil',
          error.message || 'Erro inesperado'
        );
        throw error;
      }
    },
    [updateUser, toast]
  );

  const checkAuthStatus = useCallback(async () => {
    try {
      await checkAuth();
    } catch (error: any) {
      console.error('Erro ao verificar autenticação:', error);
    }
  }, [checkAuth]);

  return {
    // Estado
    user,
    token,
    isLoading,
    isAuthenticated,
    error,
    
    // Ações
    login,
    logout,
    refreshToken: handleTokenRefresh,
    updateProfile,
    clearError,
    checkAuth: checkAuthStatus,
  };
};