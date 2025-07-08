import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User, AuthResponse, LoginCredentials } from '../types/api';
import { TOKEN_KEY, USER_KEY } from '../utils/constants';
import apiClient from '../api/client';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
}

interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  updateUser: (user: Partial<User>) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // Estado inicial
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,

      // Ações
      login: async (credentials: LoginCredentials) => {
        try {
          set({ isLoading: true, error: null });

          const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
          
          const { access_token, user } = response;

          // Salvar token e usuário
          localStorage.setItem(TOKEN_KEY, access_token);
          localStorage.setItem(USER_KEY, JSON.stringify(user));

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error: any) {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message || 'Erro ao fazer login',
          });
          throw error;
        }
      },

      logout: () => {
        // Limpar storage
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);

        // Resetar estado
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });

        // Redirecionar para login
        window.location.href = '/login';
      },

      refreshToken: async () => {
        try {
          const currentToken = get().token;
          if (!currentToken) {
            throw new Error('Não há token para renovar');
          }

          const response = await apiClient.post<AuthResponse>('/auth/refresh');
          const { access_token, user } = response;

          // Atualizar token
          localStorage.setItem(TOKEN_KEY, access_token);
          localStorage.setItem(USER_KEY, JSON.stringify(user));

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            error: null,
          });
        } catch (error: any) {
          // Se falhar, fazer logout
          get().logout();
          throw error;
        }
      },

      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          const updatedUser = { ...currentUser, ...userData };
          localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
          set({ user: updatedUser });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      checkAuth: async () => {
        try {
          set({ isLoading: true });

          const token = localStorage.getItem(TOKEN_KEY);
          const userData = localStorage.getItem(USER_KEY);

          if (!token || !userData) {
            set({ isLoading: false, isAuthenticated: false });
            return;
          }

          // Verificar se o token ainda é válido
          const user = JSON.parse(userData);
          
          try {
            // Fazer uma requisição simples para verificar se o token é válido
            await apiClient.get('/auth/me');
            
            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } catch (error) {
            // Token inválido, limpar dados
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);
            
            set({
              user: null,
              token: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });
          }
        } catch (error: any) {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message || 'Erro ao verificar autenticação',
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Hook para verificar permissões
export const usePermissions = () => {
  const user = useAuthStore((state) => state.user);

  const hasRole = (role: string) => {
    return user?.perfil === role;
  };

  const hasAnyRole = (roles: string[]) => {
    return user ? roles.includes(user.perfil) : false;
  };

  const isAdmin = () => {
    return user?.perfil === 'admin';
  };

  const isGestor = () => {
    return user?.perfil === 'gestor';
  };

  const isOperador = () => {
    return user?.perfil === 'operador';
  };

  const canAccess = (requiredRoles?: string[]) => {
    if (!requiredRoles || requiredRoles.length === 0) return true;
    return hasAnyRole(requiredRoles);
  };

  return {
    user,
    hasRole,
    hasAnyRole,
    isAdmin,
    isGestor,
    isOperador,
    canAccess,
  };
};