import { format, parseISO, isValid } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
};

export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat('pt-BR').format(value);
};

export const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value / 100);
};

export const formatDate = (date: string | Date, pattern: string = 'dd/MM/yyyy'): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return '';
    return format(dateObj, pattern, { locale: ptBR });
  } catch {
    return '';
  }
};

export const formatDateTime = (date: string | Date): string => {
  return formatDate(date, 'dd/MM/yyyy HH:mm');
};

export const formatDateTimeShort = (date: string | Date): string => {
  return formatDate(date, 'dd/MM/yy HH:mm');
};

export const formatRelativeTime = (date: string | Date): string => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    if (!isValid(dateObj)) return '';
    
    const now = new Date();
    const diff = now.getTime() - dateObj.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (minutes < 1) return 'agora';
    if (minutes < 60) return `${minutes}m atrás`;
    if (hours < 24) return `${hours}h atrás`;
    if (days < 7) return `${days}d atrás`;
    
    return formatDate(dateObj, 'dd/MM/yyyy');
  } catch {
    return '';
  }
};

export const formatCNPJ = (cnpj: string): string => {
  if (!cnpj || typeof cnpj !== 'string') return cnpj;
  const cleaned = cnpj.replace(/\D/g, '');
  if (cleaned.length !== 14) return cnpj;
  
  return cleaned.replace(
    /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
    '$1.$2.$3/$4-$5'
  );
};

export const formatCPF = (cpf: string): string => {
  if (!cpf || typeof cpf !== 'string') return cpf;
  const cleaned = cpf.replace(/\D/g, '');
  if (cleaned.length !== 11) return cpf;
  
  return cleaned.replace(
    /^(\d{3})(\d{3})(\d{3})(\d{2})$/,
    '$1.$2.$3-$4'
  );
};

export const formatPhone = (phone: string): string => {
  if (!phone || typeof phone !== 'string') return phone;
  const cleaned = phone.replace(/\D/g, '');
  
  if (cleaned.length === 10) {
    return cleaned.replace(/^(\d{2})(\d{4})(\d{4})$/, '($1) $2-$3');
  } else if (cleaned.length === 11) {
    return cleaned.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
  }
  
  return phone;
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
};

export const formatCEP = (cep: string): string => {
  if (!cep || typeof cep !== 'string') return cep;
  const cleaned = cep.replace(/\D/g, '');
  if (cleaned.length !== 8) return cep;
  
  return cleaned.replace(/^(\d{5})(\d{3})$/, '$1-$2');
};

export const formatStatus = (status: string): string => {
  const statusMap: { [key: string]: string } = {
    ativo: 'Ativo',
    inativo: 'Inativo',
    cancelado: 'Cancelado',
    suspenso: 'Suspenso',
    encerrado: 'Encerrado',
    aberta: 'Aberta',
    em_andamento: 'Em Andamento',
    encerrada: 'Encerrada',
    cancelada: 'Cancelada',
  };
  
  return statusMap[status] || status;
};

export const formatModalidade = (modalidade: string): string => {
  const modalidadeMap: { [key: string]: string } = {
    pregao_eletronico: 'Pregão Eletrônico',
    pregao_presencial: 'Pregão Presencial',
    concorrencia: 'Concorrência',
    tomada_precos: 'Tomada de Preços',
    convite: 'Convite',
    dispensa: 'Dispensa',
    inexigibilidade: 'Inexigibilidade',
  };
  
  return modalidadeMap[modalidade] || modalidade;
};

export const formatBoolean = (value: boolean): string => {
  return value ? 'Sim' : 'Não';
};

export const slugify = (text: string): string => {
  if (!text || typeof text !== 'string') return '';
  return text
    .toString()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-')
    .replace(/^-+/, '')
    .replace(/-+$/, '');
};

export const truncate = (text: string, length: number = 100): string => {
  if (!text || typeof text !== 'string') return '';
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
};

export const capitalize = (text: string): string => {
  if (!text || typeof text !== 'string') return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

export const formatInitials = (name: string): string => {
  // Guard against null/undefined/empty values
  if (!name || typeof name !== 'string') {
    return 'U'; // Default initials
  }
  
  return name
    .trim() // Remove leading/trailing spaces
    .split(' ')
    .filter(word => word.length > 0) // Remove empty strings
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .substring(0, 2);
};

export const cleanString = (text: string): string => {
  if (!text || typeof text !== 'string') return '';
  return text.replace(/[^\w\s]/gi, '').trim();
};

export const formatSearchHighlight = (text: string, search: string): string => {
  if (!text || typeof text !== 'string') return text;
  if (!search) return text;
  
  const regex = new RegExp(`(${search})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
};

export const formatErrorMessage = (error: any): string => {
  if (typeof error === 'string') return error;
  if (error?.message) return error.message;
  if (error?.detail) return error.detail;
  return 'Ocorreu um erro inesperado';
};

export const formatValidationErrors = (errors: any): { [key: string]: string } => {
  const formatted: { [key: string]: string } = {};
  
  if (Array.isArray(errors)) {
    errors.forEach((error, index) => {
      formatted[`field_${index}`] = error.msg || error.message || 'Erro de validação';
    });
  } else if (typeof errors === 'object') {
    Object.keys(errors).forEach(key => {
      formatted[key] = errors[key]?.msg || errors[key]?.message || errors[key] || 'Erro de validação';
    });
  }
  
  return formatted;
};