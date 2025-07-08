# Frontend Documentation - SEARCB

## Visão Geral

O frontend SEARCB é uma aplicação web moderna para gestão de contratações públicas, desenvolvida para integrar perfeitamente com o backend FastAPI do sistema. Este documento fornece um roadmap completo para desenvolvimento acelerado usando ferramentas de IA e boas práticas modernas.

## 1. Levantamento de Requisitos e Prototipação

### 1.1. Fluxos Principais Identificados

#### Fluxo de Autenticação
- **Login/Logout**: Tela de autenticação com validação
- **Controle de Acesso**: Redirecionamento baseado em perfis (admin, gestor, operador)
- **Gerenciamento de Sessão**: Refresh automático de tokens e logout por inatividade

#### Fluxo de Consulta e Listagem
- **PCAs**: Listagem paginada com filtros por ano, órgão, status, valor
- **Contratações**: Filtros por modalidade, situação, datas, valores
- **Atas de Registro**: Filtros por vigência, situação, valores
- **Contratos**: Filtros por fornecedor, vigência, valores
- **Usuários**: Listagem administrativa com filtros por perfil e status

#### Fluxo de Filtros Avançados
- **Filtros Contextuais**: Filtros específicos por tipo de entidade
- **Busca Livre**: Campo de busca unificado com sugestões
- **Filtros Salvos**: Possibilidade de salvar combinações de filtros
- **Exportação**: Download de resultados filtrados

#### Fluxo de Visualização de Detalhes
- **Telas de Detalhe**: Visualização completa de cada entidade
- **Histórico de Alterações**: Timeline de modificações
- **Documentos Anexos**: Visualização e download de anexos
- **Ações Contextuais**: Botões de ação baseados no perfil do usuário

#### Fluxo de Criação e Edição
- **Formulários Dinâmicos**: Validação em tempo real
- **Wizard Multi-etapas**: Para entidades complexas
- **Auto-save**: Salvamento automático de rascunhos
- **Validação Cruzada**: Validação com dados do backend

#### Fluxo de Dashboards
- **Dashboard Executivo**: Visão geral com KPIs principais
- **Dashboard Operacional**: Métricas detalhadas por área
- **Dashboard Analítico**: Gráficos e tendências temporais
- **Dashboard Personalizado**: Widgets configuráveis por usuário

#### Fluxo de Notificações
- **Notificações em Tempo Real**: Alertas via WebSocket
- **Central de Notificações**: Histórico de notificações
- **Configurações**: Preferências de notificação por usuário
- **Integração PNCP**: Notificações de atualizações externas

### 1.2. Prototipação com IA

#### Prompts para Ferramentas de Design AI

**Para Figma AI:**
```
Crie um dashboard executivo para sistema de contratações públicas com:
- Header com logo, menu de navegação e perfil do usuário
- 4 cards de KPIs: Total de Contratos, Valor Total, Contratos Vencendo, Novos PCAs
- Gráfico de barras mostrando contratações por modalidade
- Lista de últimas atividades
- Filtro de período no canto superior direito
- Layout responsivo com sidebar colapsível
```

**Para Uizard:**
```
Desenhe uma tela de listagem de contratos com:
- Barra de filtros avançados (data, valor, órgão, situação)
- Tabela paginada com colunas: número, órgão, fornecedor, valor, situação, ações
- Botões de ação: visualizar, editar, excluir
- Controles de paginação e tamanho de página
- Botão de exportar resultados
- Design moderno e limpo
```

#### Validação com Usuários-Chave

**Personas Identificadas:**
- **Administrador**: Precisa de visão completa e controles administrativos
- **Gestor**: Foco em análises e aprovações
- **Operador**: Interface simplificada para operações do dia a dia

**Método de Validação:**
- Protótipos interativos no Figma
- Sessões de feedback de 30 minutos
- Testes de usabilidade com tarefas específicas
- Iteração baseada em feedback coletado

## 2. Stack Tecnológica Recomendada

### 2.1. Framework Principal

**React com TypeScript** (Recomendado)
```bash
# Setup com Vite
npm create vite@latest searcb-frontend -- --template react-ts
cd searcb-frontend
npm install
```

**Justificativa:**
- Ecossistema maduro e suporte da comunidade
- TypeScript para maior segurança de tipos
- Integração perfeita com ferramentas de IA
- Performance otimizada com Vite

### 2.2. Gerenciamento de Estado

**Zustand** (Recomendado para simplicidade)
```bash
npm install zustand
```

**Redux Toolkit** (Para projetos mais complexos)
```bash
npm install @reduxjs/toolkit react-redux
```

### 2.3. UI Kit e Componentes

**Material UI** (Recomendado)
```bash
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install @mui/x-data-grid @mui/x-date-pickers
```

**Justificativa:**
- Componentes prontos para tabelas complexas
- Sistema de temas robusto
- Acessibilidade built-in
- Data Grid profissional

### 2.4. Comunicação com Backend

**React Query + Axios**
```bash
npm install @tanstack/react-query axios
npm install @tanstack/react-query-devtools
```

### 2.5. Autenticação e Roteamento

```bash
npm install react-router-dom
npm install @types/react-router-dom
```

### 2.6. Validação e Formulários

```bash
npm install react-hook-form @hookform/resolvers zod
```

### 2.7. Gráficos e Visualizações

```bash
npm install recharts
npm install @mui/x-charts
```

### 2.8. Testes

```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
npm install --save-dev @testing-library/user-event
```

### 2.9. Ferramentas de Desenvolvimento

```bash
npm install --save-dev eslint prettier @typescript-eslint/eslint-plugin
npm install --save-dev @storybook/react @storybook/addon-essentials
```

## 3. Integração Inteligente com Backend

### 3.1. Geração Automática de Cliente API

**Usando OpenAPI Generator:**
```bash
# Instalar OpenAPI Generator
npm install @openapitools/openapi-generator-cli

# Gerar cliente TypeScript
npx openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o src/api/generated
```

**Configuração do Cliente API:**
```typescript
// src/api/client.ts
import { Configuration, DefaultApi } from './generated';
import { getAuthToken } from '../auth/store';

const configuration = new Configuration({
  basePath: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  accessToken: () => getAuthToken(),
});

export const apiClient = new DefaultApi(configuration);
```

### 3.2. Hooks Personalizados com React Query

**Prompt para GitHub Copilot:**
```
Crie hooks React Query para todas as operações de PCA:
- usePCAs (listagem com filtros)
- usePCA (detalhes por ID)
- useCreatePCA (mutação para criar)
- useUpdatePCA (mutação para atualizar)
- useDeletePCA (mutação para deletar)
Inclua tratamento de erro e cache invalidation
```

### 3.3. Validação com Zod

**Schema Base:**
```typescript
// src/schemas/pca.ts
import { z } from 'zod';

export const PCASchema = z.object({
  ano: z.number().min(2020).max(2030),
  orgao_cnpj: z.string().length(14),
  orgao_nome: z.string().min(1),
  numero_pca: z.string().min(1),
  titulo: z.string().min(1),
  descricao: z.string().optional(),
  valor_total: z.number().positive(),
  data_publicacao: z.string().refine((date) => !isNaN(Date.parse(date))),
});

export type PCAFormData = z.infer<typeof PCASchema>;
```

## 4. Funcionalidades Principais

### 4.1. Autenticação e Controle de Acesso

#### Context de Autenticação
```typescript
// src/auth/AuthContext.tsx
interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthActions {
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}
```

#### Proteção de Rotas
```typescript
// src/components/ProtectedRoute.tsx
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: UserRole[];
  fallback?: React.ReactNode;
}
```

#### Tela de Login
**Prompt para Copilot:**
```
Crie um componente de login Material UI com:
- Formulário com email e senha
- Validação em tempo real
- Loading state durante autenticação
- Tratamento de erros
- Lembrar credenciais
- Link para recuperação de senha
```

### 4.2. Listagens e Filtros

#### Componente Base de Tabela
```typescript
// src/components/DataTable.tsx
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  pagination?: PaginationConfig;
  filters?: FilterConfig[];
  onRowClick?: (row: T) => void;
  onFilter?: (filters: FilterState) => void;
  onSort?: (sort: SortConfig) => void;
}
```

#### Filtros Avançados
**Prompt para Copilot:**
```
Crie um componente de filtros avançados reutilizável com:
- Filtros de data (range picker)
- Filtros de valor (min/max)
- Filtros de seleção (dropdown)
- Filtros de busca livre
- Botões limpar e aplicar
- Salvamento de filtros favoritos
- Estado persistente na URL
```

### 4.3. Detalhamento e CRUD

#### Tela de Detalhes Genérica
```typescript
// src/components/DetailView.tsx
interface DetailViewProps<T> {
  data: T;
  fields: FieldConfig[];
  actions?: ActionConfig[];
  tabs?: TabConfig[];
  loading?: boolean;
}
```

#### Formulários Dinâmicos
**Prompt para Copilot:**
```
Crie um sistema de formulários dinâmicos com:
- Geração de campos baseada em schema Zod
- Validação em tempo real
- Auto-save de rascunhos
- Upload de arquivos
- Campos condicionais
- Wizard multi-etapas
- Preview antes de salvar
```

### 4.4. Dashboards e Relatórios

#### Dashboard Executivo
```typescript
// src/pages/ExecutiveDashboard.tsx
interface DashboardWidget {
  id: string;
  type: 'kpi' | 'chart' | 'table' | 'list';
  title: string;
  data: any;
  config: WidgetConfig;
}
```

**Prompt para Copilot:**
```
Crie um dashboard executivo com:
- 4 cards de KPIs principais
- Gráfico de barras para modalidades
- Gráfico de linha para tendências mensais
- Lista de contratos vencendo
- Filtro de período
- Widgets redimensionáveis
- Export para PDF
```

#### Geração de Relatórios
```typescript
// src/services/reportService.ts
interface ReportConfig {
  type: 'pdf' | 'excel' | 'csv';
  template: string;
  data: any;
  filters: FilterState;
}
```

### 4.5. Notificações e Webhooks

#### Sistema de Notificações
```typescript
// src/notifications/NotificationSystem.tsx
interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actions?: NotificationAction[];
}
```

#### WebSocket para Tempo Real
```typescript
// src/services/websocketService.ts
class WebSocketService {
  private ws: WebSocket | null = null;
  
  connect(): void;
  disconnect(): void;
  subscribe(event: string, callback: Function): void;
  unsubscribe(event: string, callback: Function): void;
}
```

## 5. Uso de IA para Acelerar Desenvolvimento

### 5.1. GitHub Copilot - Prompts Estratégicos

#### Para Componentes
```
// Gerar componente completo
Crie um componente React para exibir lista de contratos com:
- Tabela Material UI com paginação
- Filtros por data, valor e status
- Ações de visualizar, editar e excluir
- Loading states e tratamento de erro
- TypeScript com interfaces apropriadas
```

#### Para Hooks Personalizados
```
// Gerar hooks React Query
Crie hooks personalizados para gerenciar estado de contratos:
- useContratos para listagem com filtros
- useContrato para buscar por ID
- useMutationContrato para CRUD operations
- Incluir cache invalidation e optimistic updates
```

#### Para Testes
```
// Gerar testes unitários
Crie testes abrangentes para o componente ContractList:
- Testes de renderização
- Testes de interação (filtros, paginação)
- Testes de integração com API
- Mock de hooks e serviços
- Casos de edge e erro
```

### 5.2. Ferramentas de Prototipação AI

#### Uizard - Prompts para Telas
```
Desenhe uma interface para gestão de PCAs com:
- Sidebar com navegação principal
- Header com busca global e notificações
- Área principal com lista filtrada de PCAs
- Painel lateral para detalhes do PCA selecionado
- Botões flutuantes para ações rápidas
- Design seguindo Material Design 3
```

#### V0.dev - Prompts para Componentes
```
Crie um card de estatísticas para dashboard com:
- Ícone à esquerda
- Título e valor principal
- Subtítulo com variação percentual
- Indicador visual de crescimento/queda
- Animação suave ao carregar
- Responsivo para mobile
```

### 5.3. IA para Documentação

#### Prompt para Documentação Automática
```
Analise este componente React e gere:
- Documentação JSDoc completa
- Exemplos de uso
- Props table para Storybook
- Casos de teste sugeridos
- Guia de acessibilidade
- Performance considerations
```

### 5.4. Assistentes de QA com IA

#### Code Review Automático
```
Revise este código React e sugira melhorias para:
- Performance (memo, callbacks, re-renders)
- Acessibilidade (ARIA, semântica)
- Segurança (XSS, validação)
- Manutenibilidade (estrutura, naming)
- Testes (cobertura, qualidade)
```

## 6. Fluxo de Desenvolvimento

### 6.1. Setup do Projeto

```bash
# 1. Criar projeto
npm create vite@latest searcb-frontend -- --template react-ts

# 2. Instalar dependências
cd searcb-frontend
npm install

# 3. Instalar dependências adicionais
npm install @mui/material @emotion/react @emotion/styled
npm install @tanstack/react-query axios zustand react-router-dom
npm install react-hook-form @hookform/resolvers zod
npm install recharts
```

#### Configuração Inicial
```typescript
// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';
import { theme } from './theme';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutos
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
```

### 6.2. Desenvolvimento por Etapas

#### Etapa 1: Autenticação (Semana 1)
- [ ] Setup do AuthContext
- [ ] Tela de login
- [ ] Proteção de rotas
- [ ] Interceptors para API
- [ ] Logout automático

#### Etapa 2: Clientes API (Semana 2)
- [ ] Geração de cliente OpenAPI
- [ ] Configuração React Query
- [ ] Hooks personalizados base
- [ ] Tratamento de erros global
- [ ] Loading states

#### Etapa 3: Listagens Principais (Semana 3-4)
- [ ] Componente DataTable base
- [ ] Sistema de filtros
- [ ] Paginação
- [ ] Ordenação
- [ ] Export de dados

#### Etapa 4: CRUD Operations (Semana 5-6)
- [ ] Formulários dinâmicos
- [ ] Validação Zod
- [ ] Telas de detalhes
- [ ] Modais de confirmação
- [ ] Feedback visual

#### Etapa 5: Dashboards (Semana 7-8)
- [ ] Dashboard executivo
- [ ] Gráficos e KPIs
- [ ] Widgets reutilizáveis
- [ ] Filtros de período
- [ ] Export de relatórios

#### Etapa 6: Notificações (Semana 9)
- [ ] Sistema de notificações
- [ ] WebSocket integration
- [ ] Configurações de usuário
- [ ] Push notifications

#### Etapa 7: Testes e QA (Semana 10)
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Testes e2e com Playwright
- [ ] Performance testing
- [ ] Acessibilidade audit

#### Etapa 8: Deploy e Documentação (Semana 11)
- [ ] CI/CD pipeline
- [ ] Storybook
- [ ] Documentação técnica
- [ ] Guias de usuário
- [ ] Performance monitoring

## 7. Exemplos de Prompts para Copilot/IA

### 7.1. Componentes React

#### Prompt: Listagem de Contratos
```
Crie um componente React para listar contratos com as seguintes funcionalidades:
- Tabela Material UI responsiva
- Filtros: data de assinatura (range), valor (min/max), situação (select), órgão (autocomplete)
- Paginação com opções de 10, 25, 50 itens por página
- Ordenação por colunas clicáveis
- Ações: visualizar (ícone eye), editar (ícone edit), excluir (ícone delete)
- Loading skeleton durante carregamento
- Estado vazio com ilustração
- Export para Excel/PDF
- Busca livre no header
- TypeScript com interfaces completas
```

#### Prompt: Formulário de PCA
```
Crie um formulário wizard multi-etapas para cadastro de PCA:
Etapa 1: Dados básicos (ano, órgão, número)
Etapa 2: Descrição e valores
Etapa 3: Itens de contratação (lista editável)
Etapa 4: Revisão e confirmação
- Validação com Zod em cada etapa
- Navegação entre etapas
- Auto-save em localStorage
- Indicador de progresso
- Botões voltar/próximo/salvar
- Confirmação antes de sair sem salvar
```

### 7.2. Hooks Personalizados

#### Prompt: Hooks de Autenticação
```
Crie um hook useAuth que gerencia:
- Estado do usuário logado
- Login/logout com persistência segura
- Refresh automático de token
- Verificação de permissões por role
- Redirect após login/logout
- Loading states
- Error handling
- Integration com React Query
- TypeScript com tipos seguros
```

#### Prompt: Hooks de Dados
```
Crie hooks React Query para gerenciar dados de contratações:
- useContratacoes: listagem com filtros, paginação, busca
- useContratacao: detalhes por ID com cache
- useCreateContratacao: mutação com optimistic updates
- useUpdateContratacao: mutação com invalidação
- useDeleteContratacao: mutação com confirmação
- Tratamento de erros consistente
- Loading states padronizados
- Cache invalidation inteligente
```

### 7.3. Dashboards e Visualizações

#### Prompt: Dashboard Executivo
```
Crie um dashboard executivo com layout responsivo:
- Grid de 4 KPIs: Total Contratos, Valor Contratado, Média Mensal, Economia Gerada
- Gráfico de barras: Contratações por modalidade (últimos 12 meses)
- Gráfico de linha: Evolução temporal de valores
- Lista: Top 10 órgãos por valor contratado
- Filtros: período, órgão, modalidade
- Widgets redimensionáveis e reordenáveis
- Export dashboard para PDF
- Atualização automática a cada 5 minutos
- Drill-down para detalhes
```

#### Prompt: Relatórios Analíticos
```
Crie um sistema de relatórios com:
- Seleção de tipo: Executivo, Operacional, Analítico
- Filtros dinâmicos baseados no tipo
- Preview em tempo real
- Geração assíncrona para relatórios grandes
- Download em múltiplos formatos (PDF, Excel, CSV)
- Agendamento de relatórios recorrentes
- Histórico de relatórios gerados
- Compartilhamento por email
```

### 7.4. Testes Automatizados

#### Prompt: Testes de Componente
```
Crie testes abrangentes para o componente ContractList:
- Rendering: renderização inicial, estados de loading/error/empty
- Interaction: filtros, paginação, ordenação, busca
- Integration: chamadas API, cache updates
- Accessibility: navegação por teclado, screen readers
- Performance: re-renders desnecessários
- Edge cases: dados inválidos, network errors
- Mocks: API responses, user interactions
- Assertions: DOM elements, state changes, function calls
```

## 8. Boas Práticas e Padrões

### 8.1. Estrutura de Projeto

```
src/
├── api/
│   ├── generated/          # Cliente OpenAPI gerado
│   ├── client.ts          # Configuração do cliente
│   └── hooks/             # React Query hooks
├── components/
│   ├── common/            # Componentes reutilizáveis
│   ├── forms/             # Componentes de formulário
│   └── ui/                # Componentes de UI base
├── pages/
│   ├── auth/              # Páginas de autenticação
│   ├── dashboard/         # Dashboards
│   └── entities/          # CRUD pages por entidade
├── hooks/
│   ├── useAuth.ts         # Hooks de autenticação
│   └── useLocalStorage.ts # Hooks utilitários
├── stores/
│   ├── authStore.ts       # Estado de autenticação
│   └── uiStore.ts         # Estado da UI
├── utils/
│   ├── constants.ts       # Constantes da aplicação
│   ├── formatters.ts      # Formatadores de dados
│   └── validators.ts      # Validadores customizados
├── styles/
│   ├── theme.ts           # Tema Material UI
│   └── globals.css        # Estilos globais
└── types/
    ├── api.ts             # Tipos da API
    └── app.ts             # Tipos da aplicação
```

### 8.2. Convenções de Nomenclatura

#### Componentes
```typescript
// PascalCase para componentes
const ContractList = () => {};
const UserProfile = () => {};

// Props com sufixo Props
interface ContractListProps {
  contracts: Contract[];
  onSelect: (contract: Contract) => void;
}
```

#### Hooks
```typescript
// Prefixo use
const useContracts = () => {};
const useAuth = () => {};
const useLocalStorage = (key: string) => {};
```

#### Constantes e Enums
```typescript
// UPPER_SNAKE_CASE para constantes
const API_BASE_URL = 'https://api.searcb.gov.br';
const DEFAULT_PAGE_SIZE = 20;

// PascalCase para enums
enum ContractStatus {
  ACTIVE = 'ACTIVE',
  EXPIRED = 'EXPIRED',
  CANCELLED = 'CANCELLED',
}
```

### 8.3. Performance e Otimização

#### Lazy Loading
```typescript
// Lazy loading de páginas
const ContractListPage = lazy(() => import('./pages/contracts/ContractList'));
const DashboardPage = lazy(() => import('./pages/dashboard/Dashboard'));

// Lazy loading de componentes pesados
const HeavyChart = lazy(() => import('./components/charts/HeavyChart'));
```

#### Memoização
```typescript
// Memoizar componentes caros
const ExpensiveComponent = memo(({ data }: Props) => {
  // Renderização custosa
});

// Memoizar callbacks
const handleClick = useCallback((id: string) => {
  // Handle click
}, [dependency]);

// Memoizar valores computados
const processedData = useMemo(() => {
  return heavyProcessing(rawData);
}, [rawData]);
```

### 8.4. Tratamento de Erros

#### Error Boundary
```typescript
// Componente Error Boundary
class ErrorBoundary extends Component {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log para serviço de monitoramento
  }
}
```

#### Hook para Tratamento de Erros
```typescript
const useErrorHandler = () => {
  return useCallback((error: Error, context?: string) => {
    console.error(`Error in ${context}:`, error);
    
    // Mostrar notificação para usuário
    toast.error(getErrorMessage(error));
    
    // Log para serviço de monitoramento
    errorTrackingService.captureException(error, { context });
  }, []);
};
```

### 8.5. Testes e Qualidade

#### Setup de Testes
```typescript
// src/setupTests.ts
import '@testing-library/jest-dom';
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

#### Mocks MSW
```typescript
// src/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/v1/contratos', (req, res, ctx) => {
    return res(
      ctx.json({
        data: mockContracts,
        total: 100,
        page: 1,
        size: 20,
      })
    );
  }),
];
```

### 8.6. Acessibilidade

#### Componentes Acessíveis
```typescript
// Componente com acessibilidade
const AccessibleButton = ({ children, onClick, ...props }: Props) => (
  <Button
    onClick={onClick}
    role="button"
    aria-label={props['aria-label']}
    tabIndex={0}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        onClick();
      }
    }}
    {...props}
  >
    {children}
  </Button>
);
```

### 8.7. Internacionalização

#### Setup i18n
```typescript
// src/i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

i18n
  .use(initReactI18next)
  .init({
    lng: 'pt-BR',
    fallbackLng: 'pt-BR',
    resources: {
      'pt-BR': {
        translation: require('./locales/pt-BR.json'),
      },
      'en': {
        translation: require('./locales/en.json'),
      },
    },
  });
```

## 9. Deploy e CI/CD

### 9.1. Build e Deploy

#### Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy Frontend

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test
      - run: npm run lint
      - run: npm run type-check

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - name: Deploy to Production
        run: |
          # Deploy steps here
```

### 9.2. Monitoramento

#### Performance Monitoring
```typescript
// src/utils/monitoring.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

const sendToAnalytics = (metric: Metric) => {
  // Enviar métricas para serviço de monitoramento
  analytics.track('web-vital', {
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
  });
};

// Medir Web Vitals
getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

## 10. Roadmap de Desenvolvimento

### Fase 1: MVP (4 semanas)
- [ ] Autenticação básica
- [ ] Listagens principais (PCA, Contratos)
- [ ] CRUD básico
- [ ] Dashboard simples

### Fase 2: Funcionalidades Avançadas (4 semanas)
- [ ] Filtros avançados
- [ ] Relatórios
- [ ] Notificações
- [ ] Integração PNCP

### Fase 3: Otimização e Qualidade (2 semanas)
- [ ] Performance optimization
- [ ] Testes abrangentes
- [ ] Acessibilidade
- [ ] Documentação

### Fase 4: Features Premium (4 semanas)
- [ ] Dashboards avançados
- [ ] IA e analytics
- [ ] Mobile app
- [ ] Integrações externas

## Contato e Suporte

Para dúvidas sobre desenvolvimento frontend:
- **Email**: dev-frontend@searcb.gov.br
- **Slack**: #frontend-searcb
- **Wiki**: https://wiki.searcb.gov.br/frontend
- **Storybook**: https://storybook.searcb.gov.br
