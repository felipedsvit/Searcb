// Tipos base da API
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  totalPages: number;
}

export interface User {
  id: number;
  email: string;
  nome: string;
  perfil: UserRole;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export const UserRole = {
  ADMIN: 'admin',
  GESTOR: 'gestor',
  OPERADOR: 'operador',
} as const;

export type UserRole = typeof UserRole[keyof typeof UserRole];

export interface PCA {
  id: number;
  ano: number;
  orgao_cnpj: string;
  orgao_nome: string;
  numero_pca: string;
  titulo: string;
  descricao?: string;
  valor_total: number;
  data_publicacao: string;
  status: PCAStatus;
  created_at: string;
  updated_at: string;
}

export const PCAStatus = {
  ATIVO: 'ativo',
  INATIVO: 'inativo',
  CANCELADO: 'cancelado',
} as const;

export type PCAStatus = typeof PCAStatus[keyof typeof PCAStatus];

export interface Contrato {
  id: number;
  numero: string;
  orgao_cnpj: string;
  orgao_nome: string;
  fornecedor_cnpj: string;
  fornecedor_nome: string;
  valor_inicial: number;
  valor_atual: number;
  data_assinatura: string;
  data_inicio: string;
  data_fim: string;
  situacao: ContractStatus;
  modalidade: string;
  objeto: string;
  created_at: string;
  updated_at: string;
}

export const ContractStatus = {
  ATIVO: 'ativo',
  ENCERRADO: 'encerrado',
  CANCELADO: 'cancelado',
  SUSPENSO: 'suspenso',
} as const;

export type ContractStatus = typeof ContractStatus[keyof typeof ContractStatus];

export interface Contratacao {
  id: number;
  numero: string;
  orgao_cnpj: string;
  orgao_nome: string;
  modalidade: string;
  situacao: ContratacaoStatus;
  objeto: string;
  valor_estimado: number;
  data_abertura: string;
  data_encerramento?: string;
  created_at: string;
  updated_at: string;
}

export const ContratacaoStatus = {
  ABERTA: 'aberta',
  EM_ANDAMENTO: 'em_andamento',
  ENCERRADA: 'encerrada',
  CANCELADA: 'cancelada',
} as const;

export type ContratacaoStatus = typeof ContratacaoStatus[keyof typeof ContratacaoStatus];

export interface Ata {
  id: number;
  numero: string;
  orgao_cnpj: string;
  orgao_nome: string;
  fornecedor_cnpj: string;
  fornecedor_nome: string;
  valor_total: number;
  data_inicio: string;
  data_fim: string;
  situacao: AtaStatus;
  objeto: string;
  created_at: string;
  updated_at: string;
}

export const AtaStatus = {
  ATIVA: 'ativa',
  ENCERRADA: 'encerrada',
  CANCELADA: 'cancelada',
} as const;

export type AtaStatus = typeof AtaStatus[keyof typeof AtaStatus];

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface FilterState {
  [key: string]: any;
}

export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

export interface PaginationConfig {
  page: number;
  size: number;
}

export interface DashboardKPI {
  title: string;
  value: number;
  change: number;
  changeType: 'increase' | 'decrease';
  format: 'number' | 'currency' | 'percentage';
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
  }[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  action: string;
  variant?: 'contained' | 'outlined' | 'text';
}

export interface ReportConfig {
  type: 'pdf' | 'excel' | 'csv';
  template: string;
  data: any;
  filters: FilterState;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}