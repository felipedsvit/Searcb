import { z } from 'zod';

export const validateCNPJ = (cnpj: string): boolean => {
  const cleaned = cnpj.replace(/\D/g, '');
  
  if (cleaned.length !== 14) return false;
  if (/^(\d)\1+$/.test(cleaned)) return false;
  
  let sum = 0;
  let weight = 2;
  
  for (let i = 11; i >= 0; i--) {
    sum += parseInt(cleaned[i]) * weight;
    weight = weight === 9 ? 2 : weight + 1;
  }
  
  const remainder = sum % 11;
  const digit1 = remainder < 2 ? 0 : 11 - remainder;
  
  if (parseInt(cleaned[12]) !== digit1) return false;
  
  sum = 0;
  weight = 2;
  
  for (let i = 12; i >= 0; i--) {
    sum += parseInt(cleaned[i]) * weight;
    weight = weight === 9 ? 2 : weight + 1;
  }
  
  const remainder2 = sum % 11;
  const digit2 = remainder2 < 2 ? 0 : 11 - remainder2;
  
  return parseInt(cleaned[13]) === digit2;
};

export const validateCPF = (cpf: string): boolean => {
  const cleaned = cpf.replace(/\D/g, '');
  
  if (cleaned.length !== 11) return false;
  if (/^(\d)\1+$/.test(cleaned)) return false;
  
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleaned[i]) * (10 - i);
  }
  
  let remainder = sum % 11;
  const digit1 = remainder < 2 ? 0 : 11 - remainder;
  
  if (parseInt(cleaned[9]) !== digit1) return false;
  
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleaned[i]) * (11 - i);
  }
  
  remainder = sum % 11;
  const digit2 = remainder < 2 ? 0 : 11 - remainder;
  
  return parseInt(cleaned[10]) === digit2;
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePhone = (phone: string): boolean => {
  const cleaned = phone.replace(/\D/g, '');
  return cleaned.length === 10 || cleaned.length === 11;
};

export const validateCEP = (cep: string): boolean => {
  const cleaned = cep.replace(/\D/g, '');
  return cleaned.length === 8;
};

export const validatePassword = (password: string): {
  isValid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];
  
  if (password.length < 8) {
    errors.push('A senha deve ter pelo menos 8 caracteres');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('A senha deve conter pelo menos uma letra maiúscula');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('A senha deve conter pelo menos uma letra minúscula');
  }
  
  if (!/\d/.test(password)) {
    errors.push('A senha deve conter pelo menos um número');
  }
  
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('A senha deve conter pelo menos um caractere especial');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
};

export const validateUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const validateDate = (date: string): boolean => {
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!dateRegex.test(date)) return false;
  
  const parsed = new Date(date);
  return !isNaN(parsed.getTime());
};

export const validateDateRange = (startDate: string, endDate: string): boolean => {
  if (!validateDate(startDate) || !validateDate(endDate)) return false;
  
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  return start <= end;
};

export const validateFileSize = (file: File, maxSizeInMB: number): boolean => {
  const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
  return file.size <= maxSizeInBytes;
};

export const validateFileType = (file: File, allowedTypes: string[]): boolean => {
  return allowedTypes.includes(file.type);
};

export const validateNumber = (value: string, min?: number, max?: number): boolean => {
  const num = parseFloat(value);
  if (isNaN(num)) return false;
  
  if (min !== undefined && num < min) return false;
  if (max !== undefined && num > max) return false;
  
  return true;
};

export const validateRequired = (value: any): boolean => {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return Boolean(value);
};

export const validateMinLength = (value: string, minLength: number): boolean => {
  return value.length >= minLength;
};

export const validateMaxLength = (value: string, maxLength: number): boolean => {
  return value.length <= maxLength;
};

export const validatePattern = (value: string, pattern: RegExp): boolean => {
  return pattern.test(value);
};

// Esquemas Zod para validação
export const userSchema = z.object({
  email: z.string().email('Email inválido'),
  nome: z.string().min(2, 'Nome deve ter pelo menos 2 caracteres'),
  perfil: z.enum(['admin', 'gestor', 'operador'], {
    required_error: 'Perfil é obrigatório',
  }),
  ativo: z.boolean().default(true),
});

export const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(1, 'Senha é obrigatória'),
});

export const pcaSchema = z.object({
  ano: z.number().min(2020).max(2030),
  orgao_cnpj: z.string().length(14, 'CNPJ deve ter 14 dígitos').refine(validateCNPJ, 'CNPJ inválido'),
  orgao_nome: z.string().min(1, 'Nome do órgão é obrigatório'),
  numero_pca: z.string().min(1, 'Número do PCA é obrigatório'),
  titulo: z.string().min(1, 'Título é obrigatório'),
  descricao: z.string().optional(),
  valor_total: z.number().positive('Valor deve ser positivo'),
  data_publicacao: z.string().refine(validateDate, 'Data inválida'),
});

export const contratoSchema = z.object({
  numero: z.string().min(1, 'Número do contrato é obrigatório'),
  orgao_cnpj: z.string().length(14, 'CNPJ deve ter 14 dígitos').refine(validateCNPJ, 'CNPJ inválido'),
  orgao_nome: z.string().min(1, 'Nome do órgão é obrigatório'),
  fornecedor_cnpj: z.string().length(14, 'CNPJ deve ter 14 dígitos').refine(validateCNPJ, 'CNPJ inválido'),
  fornecedor_nome: z.string().min(1, 'Nome do fornecedor é obrigatório'),
  valor_inicial: z.number().positive('Valor deve ser positivo'),
  valor_atual: z.number().positive('Valor deve ser positivo'),
  data_assinatura: z.string().refine(validateDate, 'Data inválida'),
  data_inicio: z.string().refine(validateDate, 'Data inválida'),
  data_fim: z.string().refine(validateDate, 'Data inválida'),
  modalidade: z.string().min(1, 'Modalidade é obrigatória'),
  objeto: z.string().min(1, 'Objeto é obrigatório'),
}).refine(data => validateDateRange(data.data_inicio, data.data_fim), {
  message: 'Data de início deve ser anterior à data de fim',
  path: ['data_fim'],
});

export const contratacaoSchema = z.object({
  numero: z.string().min(1, 'Número da contratação é obrigatório'),
  orgao_cnpj: z.string().length(14, 'CNPJ deve ter 14 dígitos').refine(validateCNPJ, 'CNPJ inválido'),
  orgao_nome: z.string().min(1, 'Nome do órgão é obrigatório'),
  modalidade: z.string().min(1, 'Modalidade é obrigatória'),
  objeto: z.string().min(1, 'Objeto é obrigatório'),
  valor_estimado: z.number().positive('Valor deve ser positivo'),
  data_abertura: z.string().refine(validateDate, 'Data inválida'),
  data_encerramento: z.string().optional().refine(
    (val) => !val || validateDate(val),
    'Data inválida'
  ),
});

export const ataSchema = z.object({
  numero: z.string().min(1, 'Número da ata é obrigatório'),
  orgao_cnpj: z.string().length(14, 'CNPJ deve ter 14 dígitos').refine(validateCNPJ, 'CNPJ inválido'),
  orgao_nome: z.string().min(1, 'Nome do órgão é obrigatório'),
  fornecedor_cnpj: z.string().length(14, 'CNPJ deve ter 14 dígitos').refine(validateCNPJ, 'CNPJ inválido'),
  fornecedor_nome: z.string().min(1, 'Nome do fornecedor é obrigatório'),
  valor_total: z.number().positive('Valor deve ser positivo'),
  data_inicio: z.string().refine(validateDate, 'Data inválida'),
  data_fim: z.string().refine(validateDate, 'Data inválida'),
  objeto: z.string().min(1, 'Objeto é obrigatório'),
}).refine(data => validateDateRange(data.data_inicio, data.data_fim), {
  message: 'Data de início deve ser anterior à data de fim',
  path: ['data_fim'],
});

export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Senha atual é obrigatória'),
  newPassword: z.string().min(8, 'Nova senha deve ter pelo menos 8 caracteres'),
  confirmPassword: z.string().min(1, 'Confirmação de senha é obrigatória'),
}).refine(data => data.newPassword === data.confirmPassword, {
  message: 'As senhas não coincidem',
  path: ['confirmPassword'],
});

export const resetPasswordSchema = z.object({
  email: z.string().email('Email inválido'),
});

export const searchSchema = z.object({
  query: z.string().min(1, 'Termo de busca é obrigatório'),
  filters: z.record(z.any()).optional(),
  sort: z.object({
    field: z.string(),
    direction: z.enum(['asc', 'desc']),
  }).optional(),
  pagination: z.object({
    page: z.number().min(1),
    size: z.number().min(1).max(100),
  }).optional(),
});

export const reportSchema = z.object({
  type: z.enum(['pdf', 'excel', 'csv']),
  template: z.string().min(1, 'Template é obrigatório'),
  filters: z.record(z.any()).optional(),
  options: z.record(z.any()).optional(),
});

export const notificationSchema = z.object({
  title: z.string().min(1, 'Título é obrigatório'),
  message: z.string().min(1, 'Mensagem é obrigatória'),
  type: z.enum(['success', 'error', 'warning', 'info']),
  recipients: z.array(z.string()).min(1, 'Pelo menos um destinatário é obrigatório'),
  scheduledAt: z.string().optional().refine(
    (val) => !val || validateDate(val),
    'Data inválida'
  ),
});