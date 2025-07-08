import type { ReactNode } from 'react';

export interface AppConfig {
  apiUrl: string;
  appName: string;
  version: string;
  environment: 'development' | 'production' | 'staging';
}

export interface RouteConfig {
  path: string;
  element: ReactNode;
  protected: boolean;
  roles?: string[];
}

export interface MenuConfig {
  title: string;
  icon: ReactNode;
  path: string;
  roles?: string[];
  children?: MenuConfig[];
}

export interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, row: T) => ReactNode;
  width?: number;
  align?: 'left' | 'center' | 'right';
}

export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

export interface PaginationConfig {
  page: number;
  size: number;
}

export interface FilterConfig {
  key: string;
  label: string;
  type: 'text' | 'select' | 'date' | 'daterange' | 'number' | 'numberrange';
  options?: { value: any; label: string }[];
  placeholder?: string;
}

export interface FieldConfig {
  key: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'select' | 'textarea' | 'checkbox' | 'file';
  required?: boolean;
  options?: { value: any; label: string }[];
  validation?: any;
  placeholder?: string;
  helperText?: string;
}

export interface ActionConfig {
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  variant?: 'contained' | 'outlined' | 'text';
  disabled?: boolean;
}

export interface TabConfig {
  label: string;
  content: ReactNode;
  icon?: ReactNode;
}

export interface WidgetConfig {
  id: string;
  type: 'kpi' | 'chart' | 'table' | 'list';
  title: string;
  size: { width: number; height: number };
  position: { x: number; y: number };
  data: any;
  refreshInterval?: number;
}

export interface ThemeConfig {
  mode: 'light' | 'dark';
  primaryColor: string;
  secondaryColor: string;
  fontSize: 'small' | 'medium' | 'large';
}

export interface UserPreferences {
  theme: ThemeConfig;
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    desktop: boolean;
  };
  dashboard: {
    widgets: WidgetConfig[];
    autoRefresh: boolean;
    refreshInterval: number;
  };
}

export interface FormState {
  values: { [key: string]: any };
  errors: { [key: string]: string };
  touched: { [key: string]: boolean };
  isValid: boolean;
  isSubmitting: boolean;
}

export interface DataTableState {
  loading: boolean;
  data: any[];
  total: number;
  page: number;
  pageSize: number;
  sortField?: string;
  sortDirection?: 'asc' | 'desc';
  filters: { [key: string]: any };
  selectedRows: any[];
}

export interface NavigationItem {
  id: string;
  label: string;
  icon?: ReactNode;
  path?: string;
  onClick?: () => void;
  children?: NavigationItem[];
  roles?: string[];
  disabled?: boolean;
}

export interface BreadcrumbItem {
  label: string;
  path?: string;
  icon?: ReactNode;
}

export interface ErrorInfo {
  message: string;
  code?: string;
  details?: any;
  timestamp: Date;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
}

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  actions?: {
    label: string;
    action: () => void;
  }[];
}

export interface Modal {
  id: string;
  title: string;
  content: ReactNode;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  closable?: boolean;
  onClose?: () => void;
  actions?: ActionConfig[];
}

export interface ApiError {
  message: string;
  status: number;
  code?: string;
  details?: any;
}

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
}

export interface SelectOption {
  value: any;
  label: string;
  disabled?: boolean;
  group?: string;
}

export interface FileUpload {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  url?: string;
  error?: string;
}