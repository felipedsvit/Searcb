export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const APP_NAME = 'SEARCB';
export const APP_VERSION = '1.0.0';

export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

export const TOKEN_KEY = 'searcb_token';
export const USER_KEY = 'searcb_user';
export const THEME_KEY = 'searcb_theme';

export const ROLES = {
  ADMIN: 'admin',
  GESTOR: 'gestor',
  OPERADOR: 'operador',
} as const;

export const PERMISSIONS = {
  CREATE_USER: 'create_user',
  EDIT_USER: 'edit_user',
  DELETE_USER: 'delete_user',
  VIEW_ADMIN: 'view_admin',
  MANAGE_SYSTEM: 'manage_system',
  EXPORT_DATA: 'export_data',
  GENERATE_REPORTS: 'generate_reports',
} as const;

export const ROLE_PERMISSIONS = {
  [ROLES.ADMIN]: [
    PERMISSIONS.CREATE_USER,
    PERMISSIONS.EDIT_USER,
    PERMISSIONS.DELETE_USER,
    PERMISSIONS.VIEW_ADMIN,
    PERMISSIONS.MANAGE_SYSTEM,
    PERMISSIONS.EXPORT_DATA,
    PERMISSIONS.GENERATE_REPORTS,
  ],
  [ROLES.GESTOR]: [
    PERMISSIONS.VIEW_ADMIN,
    PERMISSIONS.EXPORT_DATA,
    PERMISSIONS.GENERATE_REPORTS,
  ],
  [ROLES.OPERADOR]: [
    PERMISSIONS.EXPORT_DATA,
  ],
} as const;

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  PCAS: '/pcas',
  CONTRATOS: '/contratos',
  CONTRATACOES: '/contratacoes',
  ATAS: '/atas',
  USUARIOS: '/usuarios',
  RELATORIOS: '/relatorios',
  CONFIGURACOES: '/configuracoes',
  PERFIL: '/perfil',
} as const;

export const STATUS_COLORS = {
  ativo: 'success',
  inativo: 'warning',
  cancelado: 'error',
  aberta: 'info',
  em_andamento: 'warning',
  encerrada: 'success',
  cancelada: 'error',
  suspenso: 'warning',
} as const;

export const MODALIDADES = [
  { value: 'pregao_eletronico', label: 'Pregão Eletrônico' },
  { value: 'pregao_presencial', label: 'Pregão Presencial' },
  { value: 'concorrencia', label: 'Concorrência' },
  { value: 'tomada_precos', label: 'Tomada de Preços' },
  { value: 'convite', label: 'Convite' },
  { value: 'dispensa', label: 'Dispensa' },
  { value: 'inexigibilidade', label: 'Inexigibilidade' },
] as const;

export const SITUACOES = [
  { value: 'ativo', label: 'Ativo' },
  { value: 'inativo', label: 'Inativo' },
  { value: 'cancelado', label: 'Cancelado' },
  { value: 'suspenso', label: 'Suspenso' },
  { value: 'encerrado', label: 'Encerrado' },
] as const;

export const DATE_FORMATS = {
  DISPLAY: 'DD/MM/YYYY',
  DISPLAY_WITH_TIME: 'DD/MM/YYYY HH:mm',
  API: 'YYYY-MM-DD',
  API_WITH_TIME: 'YYYY-MM-DD HH:mm:ss',
} as const;

export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
} as const;

export const CHART_COLORS = [
  '#1976d2',
  '#dc004e',
  '#ed6c02',
  '#2e7d32',
  '#9c27b0',
  '#00acc1',
  '#d32f2f',
  '#1565c0',
  '#7b1fa2',
  '#00838f',
] as const;

export const WEBSOCKET_EVENTS = {
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  USER_ACTIVITY: 'user_activity',
  NOTIFICATION: 'notification',
  DATA_UPDATE: 'data_update',
  SYSTEM_ALERT: 'system_alert',
} as const;

export const EXPORT_FORMATS = {
  PDF: 'pdf',
  EXCEL: 'excel',
  CSV: 'csv',
} as const;

export const VALIDATION_MESSAGES = {
  REQUIRED: 'Este campo é obrigatório',
  EMAIL: 'Email inválido',
  MIN_LENGTH: 'Mínimo de {min} caracteres',
  MAX_LENGTH: 'Máximo de {max} caracteres',
  INVALID_CNPJ: 'CNPJ inválido',
  INVALID_CPF: 'CPF inválido',
  INVALID_DATE: 'Data inválida',
  INVALID_NUMBER: 'Número inválido',
  PASSWORD_MISMATCH: 'As senhas não coincidem',
} as const;

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  THEME: 'theme',
  PREFERENCES: 'preferences',
  FILTERS: 'filters',
  DASHBOARD_CONFIG: 'dashboard_config',
} as const;

export const TIMEOUTS = {
  DEFAULT_REQUEST: 10000,
  LONG_REQUEST: 30000,
  WEBSOCKET_RECONNECT: 5000,
  NOTIFICATION_DURATION: 5000,
} as const;

export const LIMITS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  MAX_EXPORT_ROWS: 10000,
  MAX_SEARCH_RESULTS: 1000,
  MAX_CONCURRENT_REQUESTS: 5,
} as const;