import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Toast, Modal, LoadingState } from '../types/app';

interface UIState {
  // Sidebar
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  
  // Theme
  darkMode: boolean;
  
  // Loading
  globalLoading: LoadingState;
  
  // Notificações/Toasts
  toasts: Toast[];
  
  // Modais
  modals: Modal[];
  
  // Breadcrumbs
  breadcrumbs: { label: string; path?: string }[];
  
  // Page title
  pageTitle: string;
}

interface UIActions {
  // Sidebar actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebarCollapse: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  
  // Theme actions
  toggleDarkMode: () => void;
  setDarkMode: (dark: boolean) => void;
  
  // Loading actions
  setGlobalLoading: (loading: LoadingState) => void;
  clearGlobalLoading: () => void;
  
  // Toast actions
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  
  // Modal actions
  openModal: (modal: Omit<Modal, 'id'>) => void;
  closeModal: (id: string) => void;
  closeAllModals: () => void;
  
  // Breadcrumb actions
  setBreadcrumbs: (breadcrumbs: { label: string; path?: string }[]) => void;
  
  // Page title actions
  setPageTitle: (title: string) => void;
}

export const useUIStore = create<UIState & UIActions>()(
  persist(
    (set, get) => ({
      // Estado inicial
      sidebarOpen: true,
      sidebarCollapsed: false,
      darkMode: false,
      globalLoading: { isLoading: false },
      toasts: [],
      modals: [],
      breadcrumbs: [],
      pageTitle: 'SEARCB',

      // Sidebar actions
      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }));
      },

      setSidebarOpen: (open: boolean) => {
        set({ sidebarOpen: open });
      },

      toggleSidebarCollapse: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
      },

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed });
      },

      // Theme actions
      toggleDarkMode: () => {
        set((state) => ({ darkMode: !state.darkMode }));
      },

      setDarkMode: (dark: boolean) => {
        set({ darkMode: dark });
      },

      // Loading actions
      setGlobalLoading: (loading: LoadingState) => {
        set({ globalLoading: loading });
      },

      clearGlobalLoading: () => {
        set({ globalLoading: { isLoading: false } });
      },

      // Toast actions
      addToast: (toast: Omit<Toast, 'id'>) => {
        const id = Date.now().toString();
        const newToast: Toast = {
          ...toast,
          id,
          duration: toast.duration ?? 5000,
        };

        set((state) => ({
          toasts: [...state.toasts, newToast],
        }));

        // Auto-remove toast após a duração especificada
        if (newToast.duration && newToast.duration > 0) {
          setTimeout(() => {
            get().removeToast(id);
          }, newToast.duration);
        }
      },

      removeToast: (id: string) => {
        set((state) => ({
          toasts: state.toasts.filter((toast) => toast.id !== id),
        }));
      },

      clearToasts: () => {
        set({ toasts: [] });
      },

      // Modal actions
      openModal: (modal: Omit<Modal, 'id'>) => {
        const id = Date.now().toString();
        const newModal: Modal = {
          ...modal,
          id,
          size: modal.size ?? 'md',
          closable: modal.closable ?? true,
        };

        set((state) => ({
          modals: [...state.modals, newModal],
        }));
      },

      closeModal: (id: string) => {
        set((state) => ({
          modals: state.modals.filter((modal) => modal.id !== id),
        }));
      },

      closeAllModals: () => {
        set({ modals: [] });
      },

      // Breadcrumb actions
      setBreadcrumbs: (breadcrumbs: { label: string; path?: string }[]) => {
        set({ breadcrumbs });
      },

      // Page title actions
      setPageTitle: (title: string) => {
        set({ pageTitle: title });
        document.title = `${title} - SEARCB`;
      },
    }),
    {
      name: 'ui-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        darkMode: state.darkMode,
      }),
    }
  )
);

// Hook utilitário para toasts
export const useToast = () => {
  const addToast = useUIStore((state) => state.addToast);

  const toast = {
    success: (title: string, message: string, duration?: number) => {
      addToast({ type: 'success', title, message, duration });
    },
    error: (title: string, message: string, duration?: number) => {
      addToast({ type: 'error', title, message, duration });
    },
    warning: (title: string, message: string, duration?: number) => {
      addToast({ type: 'warning', title, message, duration });
    },
    info: (title: string, message: string, duration?: number) => {
      addToast({ type: 'info', title, message, duration });
    },
  };

  return toast;
};

// Hook utilitário para modais
export const useModal = () => {
  const { openModal, closeModal, closeAllModals } = useUIStore();

  const modal = {
    open: openModal,
    close: closeModal,
    closeAll: closeAllModals,
    confirm: (
      title: string,
      message: string,
      onConfirm: () => void,
      onCancel?: () => void
    ) => {
      openModal({
        title,
        content: message,
        actions: [
          {
            label: 'Cancelar',
            onClick: () => {
              closeAllModals();
              onCancel?.();
            },
            color: 'secondary',
            variant: 'outlined',
          },
          {
            label: 'Confirmar',
            onClick: () => {
              closeAllModals();
              onConfirm();
            },
            color: 'primary',
            variant: 'contained',
          },
        ],
      });
    },
  };

  return modal;
};