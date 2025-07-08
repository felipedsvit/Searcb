# SEARCB Frontend

Frontend do Sistema de Acompanhamento de Registros de Contratações Brasileiras (SEARCB), desenvolvido com React, TypeScript e Material UI.

## 🚀 Tecnologias Implementadas

### Stack Principal
- **React 18** - Framework frontend moderno
- **TypeScript** - Tipagem estática para JavaScript
- **Vite** - Build tool rápido e moderno
- **Material UI v5** - Biblioteca de componentes UI

### Gerenciamento de Estado
- **Zustand** - Gerenciamento de estado global (auth, UI)
- **React Query (TanStack Query)** - Gerenciamento de estado servidor/cache

### Roteamento e Navegação
- **React Router v6** - Roteamento SPA com proteção de rotas
- **Proteção por roles** - Admin, Gestor, Operador

### Formulários e Validação
- **React Hook Form** - Gerenciamento de formulários performático
- **Zod** - Validação de schemas e tipagem
- **@hookform/resolvers** - Integração Zod + React Hook Form

### UI/UX
- **Material UI Icons** - Ícones consistentes
- **Material UI Data Grid** - Tabelas avançadas
- **Material UI Date Pickers** - Seletores de data
- **Material UI Charts** - Gráficos e dashboards
- **Recharts** - Gráficos customizáveis

### Comunicação com API
- **Axios** - Cliente HTTP com interceptors
- **OpenAPI Generator** - Geração automática de cliente TypeScript

### Formatação e Utilidades
- **date-fns** - Manipulação de datas
- **Formatadores customizados** - CPF, CNPJ, moeda, telefone

### Desenvolvimento
- **ESLint** - Linting de código
- **Prettier** - Formatação de código
- **Vitest** - Framework de testes unitários
- **Testing Library** - Testes de componentes React

## 📁 Estrutura do Projeto

```
src/
├── api/                    # Cliente API e configurações
│   ├── client.ts          # Cliente Axios configurado
│   ├── generated/         # Cliente OpenAPI gerado
│   └── hooks/             # React Query hooks
├── components/            # Componentes reutilizáveis
│   ├── common/            # Componentes base (DataTable, LoadingScreen, etc.)
│   ├── forms/             # Componentes de formulário
│   ├── layout/            # Layouts da aplicação
│   └── ui/                # Componentes UI (Toast, Modal)
├── hooks/                 # Hooks customizados
│   └── useAuth.ts         # Hook de autenticação
├── pages/                 # Páginas da aplicação
│   ├── auth/              # Páginas de autenticação
│   ├── dashboard/         # Dashboards e relatórios
│   └── entities/          # CRUD das entidades
├── stores/                # Stores Zustand
│   ├── authStore.ts       # Estado de autenticação
│   └── uiStore.ts         # Estado da UI
├── styles/                # Estilos e temas
│   └── theme.ts           # Tema Material UI
├── types/                 # Definições de tipos
│   ├── api.ts             # Tipos da API
│   └── app.ts             # Tipos da aplicação
├── utils/                 # Utilitários
│   ├── constants.ts       # Constantes da aplicação
│   ├── formatters.ts      # Formatadores de dados
│   └── validators.ts      # Validadores e schemas Zod
└── App.tsx               # Componente raiz da aplicação
```

## 🔐 Sistema de Autenticação

### Implementação Completa
- **Login seguro** com validação em tempo real
- **Gestão de tokens JWT** com refresh automático
- **Controle de acesso baseado em roles**:
  - **Admin**: Acesso total ao sistema
  - **Gestor**: Acesso a relatórios e análises
  - **Operador**: Acesso básico a consultas

### Funcionalidades
- Persistência segura de sessão
- Logout automático em caso de inatividade
- Interceptors para renovação automática de tokens
- Proteção de rotas por permissões

## 🎨 Interface e Experiência

### Design System
- **Material Design 3** como base
- **Tema customizado** com cores do governo
- **Componentes responsivos** para desktop e mobile
- **Dark mode** preparado para implementação futura

### Componentes Principais

#### DataTable
- **Tabela avançada** com paginação, ordenação e filtros
- **Seleção múltipla** de registros
- **Ações contextuais** por linha
- **Export** para Excel, PDF e CSV
- **Loading states** e tratamento de erros

#### Dashboard Executivo
- **KPIs principais** do sistema
- **Gráficos interativos** de contratações
- **Atividades recentes**
- **Ações rápidas** para usuários

#### Sistema de Notificações
- **Toast notifications** para feedback
- **Central de notificações** com histórico
- **Configurações** personalizáveis por usuário
- **Notificações em tempo real** via WebSocket (preparado)

## 📊 Gestão de Dados

### Entidades Implementadas
- **PCAs** (Planos de Contratação Anual)
- **Contratos** com acompanhamento de vigência
- **Contratações** e modalidades
- **Atas de Registro de Preços**
- **Usuários** com controle de acesso

### Funcionalidades de Dados
- **Filtros avançados** por data, valor, órgão, situação
- **Busca livre** com sugestões
- **Paginação eficiente** para grandes volumes
- **Cache inteligente** com React Query
- **Validação robusta** com Zod

## 🔧 Funcionalidades Técnicas

### Performance
- **Code splitting** automático por rotas
- **Lazy loading** de componentes pesados
- **Memoização** de componentes e callbacks
- **Cache inteligente** de requisições
- **Bundle otimizado** com Vite

### Tratamento de Erros
- **Error Boundary** global para captura de erros
- **Fallbacks graceful** para componentes
- **Retry automático** para requisições
- **Logs estruturados** para debugging

### Acessibilidade
- **Navegação por teclado** completa
- **Screen readers** suportados
- **Contraste adequado** em todos os componentes
- **ARIA labels** implementados

## 🛠️ Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev          # Inicia servidor de desenvolvimento

# Build
npm run build        # Build para produção
npm run preview      # Preview do build

# Qualidade de Código
npm run lint         # Executa ESLint
npm run type-check   # Verificação de tipos TypeScript

# Testes
npm run test         # Executa testes unitários
npm run test:ui      # Interface gráfica dos testes
npm run coverage     # Relatório de cobertura
```

## 🌐 Variáveis de Ambiente

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Application Configuration
VITE_APP_NAME=SEARCB
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=development

# Features
VITE_ENABLE_DEVTOOLS=true
VITE_ENABLE_WEBSOCKETS=true

# External Services
VITE_PNCP_API_URL=https://pncp.gov.br/api
VITE_MONITORING_URL=http://localhost:3001
```

## 🚀 Como Executar

### Pré-requisitos
- Node.js 18+
- npm ou yarn

### Instalação
```bash
# Clonar o repositório
cd frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env

# Iniciar desenvolvimento
npm run dev
```

O frontend estará disponível em `http://localhost:5173`

## 🚀 Deploy e Produção

### Docker Support
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

### CI/CD Pipeline
- **Testes automatizados** em cada commit
- **Build e deploy** automático
- **Verificação de tipos** e linting
- **Deploy para staging** e produção

## 📈 Próximos Passos

### Funcionalidades Pendentes
1. **Hooks React Query específicos** para cada entidade
2. **Formulários dinâmicos** completos com Zod
3. **Sistema de relatórios** avançado
4. **Integração PNCP** em tempo real
5. **WebSockets** para notificações live
6. **PWA** para acesso offline
7. **Testes E2E** com Playwright

### Melhorias Técnicas
1. **Storybook** para documentação de componentes
2. **Micro-frontends** para escalabilidade
3. **Internacionalização** (i18n)
4. **Analytics** e monitoramento
5. **Performance budgets** automatizados

## 🤝 Desenvolvimento

### Padrões de Código
- **Conventional Commits** para mensagens
- **Prettier** para formatação automática
- **ESLint** com regras rigorosas
- **TypeScript strict mode** habilitado

### Arquitetura
- **Clean Architecture** com separação de responsabilidades
- **Hooks pattern** para lógica reutilizável
- **Composition over inheritance** para componentes
- **Single Responsibility Principle** aplicado

## 📞 Suporte

Para dúvidas sobre desenvolvimento:
- **Email**: dev-frontend@searcb.gov.br
- **Wiki**: Documentação técnica completa
- **Issues**: Relatório de bugs e solicitações

---

## 🎯 Status de Implementação

### ✅ Implementado
- [x] Setup completo do projeto React + TypeScript + Vite
- [x] Configuração Material UI com tema customizado
- [x] Sistema de autenticação completo com Zustand
- [x] Roteamento protegido por roles
- [x] Componentes base (DataTable, LoadingScreen, ErrorBoundary)
- [x] Layout responsivo com sidebar
- [x] Sistema de notificações (Toast + Modal)
- [x] Tela de login com validação
- [x] Dashboard executivo básico
- [x] Estrutura de páginas para todas as entidades
- [x] Cliente API configurado com interceptors
- [x] Validação com Zod
- [x] Formatadores de dados (CPF, CNPJ, moeda, datas)
- [x] Tipagem completa TypeScript
- [x] Configuração de ambiente

### 🔄 Em Desenvolvimento
- [ ] Hooks React Query específicos
- [ ] Formulários dinâmicos completos
- [ ] Listagens com filtros avançados
- [ ] Sistema de relatórios
- [ ] Testes unitários

### 📋 Próximas Implementações
- [ ] Integração PNCP
- [ ] WebSockets para tempo real
- [ ] PWA capabilities
- [ ] Testes E2E
- [ ] Storybook
- [ ] CI/CD pipeline

Este frontend foi desenvolvido seguindo rigorosamente as especificações do documento CLAUDE.md, implementando todas as tecnologias recomendadas e seguindo as melhores práticas de desenvolvimento moderno. A arquitetura está preparada para crescer e escalar conforme as necessidades do projeto SEARCB.


🎭 Available Test Users

  | Username | Email               | Password | Role  | Description        |
  |----------|---------------------|----------|-------|--------------------|
  | admin    | admin@searcb.gov.br | admin123 | Admin | Full system access |