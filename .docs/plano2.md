# Plano Detalhado: Plataforma nRadar (MVP Refinado)

A nRadar será uma plataforma de inteligência de mercado e alertas que conecta fornecedores a oportunidades de licitação, monitorando continuamente o Portal Nacional de Contratações Públicas (PNCP) via API.

## 1. Onboarding e Cadastro do Usuário

O objetivo desta etapa é oferecer um processo de entrada rápido e descomplicado para que o usuário possa começar a configurar seus interesses o mais breve possível.

- **Cadastro Padrão:** Manter a funcionalidade de cadastro via e-mail e senha, com verificação de e-mail para garantir a validade do contato.
- **Login Social:** Implementar login com provedores populares como Google e LinkedIn. Isso reduz a fricção, agiliza o acesso e aumenta a taxa de conversão de cadastros.
- **Perfil Básico:** Após o primeiro login, o usuário preencherá informações básicas, como nome da empresa, CNPJ e área de atuação principal, que podem ser usadas para sugerir configurações de radar iniciais.

## 2. Criação e Gerenciamento de Perfis de Interesse (Radar)

Esta é a funcionalidade central da plataforma. Um "Radar" é um conjunto de filtros salvos que busca ativamente por novas oportunidades. O usuário poderá criar múltiplos radares para diferentes estratégias de negócio.

### Campos de Configuração do Perfil (Radar):
- **Nome do Perfil:** Campo de texto para identificar facilmente cada radar (ex: "Licitações de TI - São Paulo", "Serviços de Engenharia - Nordeste").
- **Palavras-chave:** Campo de texto para inserir termos que serão buscados no objeto da contratação e informações complementares (`objetoCompra`, `informacaoComplementar`).
- **Localização:**
  - **Estado (UF):** Seletor múltiplo para escolher um ou mais estados de interesse. Utiliza o parâmetro `uf` da API.
  - **Município:** Seletor múltiplo que permite pesquisar e adicionar municípios. Utiliza o parâmetro `codigoMunicipioIbge`.
- **Modalidades de Contratação:** Lista de checkboxes baseada na tabela de domínio "Modalidade de Contratação" (Seção 5.2 do manual). O sistema usará os códigos correspondentes para filtrar as buscas via API (`codigoModalidadeContratacao`). Exemplos:
  - Leilão (Eletrônico/Presencial)
  - Diálogo Competitivo
  - Concurso
  - Concorrência (Eletrônica/Presencial)
  - Pregão (Eletrônico/Presencial)
  - Dispensa de Licitação
  - Inexigibilidade
  - Credenciamento
- **Categorias do Produto/Serviço:** Lista de checkboxes baseada na tabela "Categoria do Processo" (Seção 5.11 do manual):
  - Compras
  - Informática (TIC)
  - Obras
  - Serviços de Engenharia
  - Serviços de Saúde
  - Mão de Obra
  - Locação Imóveis
- **Filtro de Urgência:** Seletor de opção única para classificar a proximidade do prazo final, com base no campo `dataEncerramentoProposta` retornado pela API:
  - Urgente: Oportunidades que encerram em até 3 dias.
  - Próxima Semana: Oportunidades que encerram em até 7 dias.
  - Qualquer Prazo: Exibir todas as oportunidades, independentemente do prazo.

## 3. Configuração de Notificações

Para garantir que os usuários não percam nenhuma oportunidade, o sistema de notificação deve ser flexível e personalizável para cada radar criado.

- **Canais de Notificação:** Para cada radar, o usuário poderá habilitar ou desabilitar independentemente:
  - Notificações por E-mail: Um resumo diário ou alertas instantâneos com as novas oportunidades encontradas.
  - Notificações Push (Mobile): Alertas em tempo real enviados para o aplicativo móvel da nRadar.
- **Gerenciamento Centralizado:** Uma tela de "Configurações de Notificação" permitirá ao usuário visualizar e ajustar as preferências de todos os seus radares em um único lugar.

## 4. Sistema de Feed de Oportunidades

O feed é a tela principal onde os resultados dos radares ativos são exibidos de forma clara e organizada.

- **Visualização Agregada:** O feed principal exibirá uma lista cronológica de todas as oportunidades que correspondem a qualquer um dos radares ativos do usuário.
- **Filtragem por Radar:** O usuário poderá filtrar o feed para visualizar oportunidades de um radar específico.
- **Card Resumido da Oportunidade:** Cada oportunidade será exibida em um card contendo informações essenciais extraídas da API, como:
  - Objeto da Contratação: `objetoCompra`
  - Órgão/Entidade: `orgaoEntidade.razaosocial`
  - Localização: `unidadeOrgao.municipioNome - unidadeOrgao.ufSigla`
  - Modalidade: `modalidadeNome`
  - Data de Encerramento: `dataEncerramentoProposta`, com um selo visual de urgência ("Urgente", "Encerra Hoje")

## 5. Tela de Detalhes da Oportunidade

Ao clicar em um card, o usuário acessará uma página com todas as informações disponíveis sobre a licitação, extraídas diretamente da API do PNCP para garantir a precisão.

- **Informações Completas:** A tela exibirá todos os dados relevantes retornados pelo serviço Consultar Contratações com Período de Recebimento de Propostas em Aberto:
  - Identificação: Nº do Controle PNCP (`numeroControlePNCP`), Nº da Compra (`numeroCompra`), Processo (`processo`).
  - Descrição: Objeto completo (`objetoCompra`) e Informações Complementares (`informacaoComplementar`).
  - Datas e Prazos: Data de Abertura (`dataAberturaProposta`) e Encerramento (`dataEncerramentoProposta`).
  - Valores: Valor Total Estimado (`valorTotalEstimado`).
  - Dados do Órgão: Razão Social (`orgaoEntidade.razaosocial`), CNPJ, Unidade (`unidadeOrgao.nomeUnidade`).
  - Link Direto: Um botão de destaque com o `linkSistemaOrigem` para que o usuário possa acessar a página original da licitação, onde poderá obter os editais e enviar sua proposta.

## Recomendações para Otimização de Usabilidade e Precisão

Para diferenciar a nRadar e entregar uma experiência superior, considere as seguintes otimizações:

- **Melhorar a Precisão dos Filtros:**
  - Busca Avançada: Permita o uso de operadores booleanos nas palavras-chave (ex: desenvolvimento E "aplicativo móvel" NÃO manutenção) para refinar os resultados.
  - Aproveitar Filtros Adicionais da API: Incorpore filtros para `srp` (Sistema de Registro de Preços) e `tipoInstrumentoConvocatorioNome` (Edital, Aviso de Contratação Direta, etc.), campos disponíveis na API que podem ser cruciais para certos nichos de mercado.
- **Otimizar a Usabilidade:**
  - Onboarding Guiado: Crie um "wizard" passo a passo que ajude o novo usuário a configurar seu primeiro radar, explicando cada campo.
  - Templates de Radar: Ofereça perfis pré-configurados para setores comuns (ex: "Construção Civil", "Material de Escritório", "Software como Serviço") que os usuários possam ativar e personalizar.
  - Feedback nas Oportunidades: Permita que os usuários marquem uma oportunidade como "Relevante" ou "Não relevante". Use essa informação para, futuramente, sugerir melhorias nos filtros do radar ou até mesmo treinar um modelo de recomendação.

## Visão de Futuro (Além do MVP)

- **Inteligência de Longo Prazo com PCA:** Desenvolva uma funcionalidade que monitore o Plano de Contratações Anual (PCA) usando os serviços 6.1 e 6.2 do manual. Isso permitirá que seus usuários se antecipem às futuras licitações, preparando-se com meses de antecedência.
- **Análise de Concorrência:** Analise dados de licitações passadas e atas de registro de preços (Serviço 6.5) para fornecer insights sobre quais empresas estão vencendo licitações em determinados segmentos e a que preços.

---

*Se precisar detalhar ainda mais alguma dessas seções, é só pedir.*

# Comandos e Exemplos Técnicos

## Exemplo de Estrutura docker compose.yml

```yaml
version: "3.9"

networks:
  pncp-net:
    driver: bridge

volumes:
  db-data:
  grafana-data:

services:
  nginx:
    image: nginx:stable-alpine
    container_name: reverse-proxy
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certs:/etc/nginx/certs
# ...demais serviços...
```

## Exemplo de Configuração Inicial do Vite

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
2. Configuração do Tailwind


// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        success: {
          50: '#ecfdf5',
          500: '#10b981',
          600: '#059669',
        },
        warning: {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        },
        danger: {
          50: '#fef2f2',
          500: '#ef4444',
          600: '#dc2626',
        },
      },
    },
  },
  plugins: [],
}
Definições de Tipos


// types/index.ts
export interface User {
  id: string;
  email: string;
  name: string;
  companyName?: string;
  cnpj?: string;
  role: 'user' | 'admin';
}

export interface Radar {
  id: string;
  name: string;
  keywords: string[];
  locations: {
    states: string[];
    cities: string[];
  };
  contractModalities: number[];
  categories: number[];
  urgencyFilter: 'urgent' | 'week' | 'any';
  notifications: {
    email: boolean;
    push: boolean;
  };
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Opportunity {
  id: string;
  numeroControlePNCP: string;
  objetoCompra: string;
  modalidadeNome: string;
  valorTotalEstimado: number;
  dataEncerramentoProposta: string;
  orgaoEntidade: {
    razaoSocial: string;
    cnpj: string;
  };
  unidadeOrgao: {
    municipioNome: string;
    ufSigla: string;
  };
  linkSistemaOrigem: string;
  urgency: 'urgent' | 'week' | 'normal';
  radarId: string;
}
Estrutura de Rotas


// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '@/contexts/AuthContext'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Layout } from '@/components/layout/Layout'

// Pages
import { Landing } from '@/pages/Landing'
import { Login } from '@/pages/auth/Login'
import { Register } from '@/pages/auth/Register'
import { Dashboard } from '@/pages/Dashboard'
import { Radars } from '@/pages/radars/Radars'
import { CreateRadar } from '@/pages/radars/CreateRadar'
import { EditRadar } from '@/pages/radars/EditRadar'
import { Feed } from '@/pages/Feed'
import { OpportunityDetails } from '@/pages/OpportunityDetails'
import { Settings } from '@/pages/Settings'
import { Profile } from '@/pages/Profile'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutos
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Rotas públicas */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Rotas protegidas */}
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/feed" element={<Feed />} />
                <Route path="/opportunity/:id" element={<OpportunityDetails />} />
                
                {/* Rotas de Radars */}
                <Route path="/radars" element={<Radars />} />
                <Route path="/radars/create" element={<CreateRadar />} />
                <Route path="/radars/:id/edit" element={<EditRadar />} />
                
                {/* Configurações */}
                <Route path="/settings" element={<Settings />} />
                <Route path="/profile" element={<Profile />} />
              </Route>
            </Route>
          </Routes>
          <Toaster position="top-right" />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}
Hooks Personalizados

1. Hook de Autenticação


// hooks/useAuth.ts
import { useContext } from 'react'
import { AuthContext } from '@/contexts/AuthContext'

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
2. Hook para Radars


// hooks/useRadars.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { radarService } from '@/services/radarService'
import { Radar } from '@/types'

export const useRadars = () => {
  return useQuery({
    queryKey: ['radars'],
    queryFn: radarService.getAll,
  })
}

export const useCreateRadar = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: radarService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['radars'] })
      toast.success('Radar criado com sucesso!')
    },
    onError: (error) => {
      toast.error('Erro ao criar radar: ' + error.message)
    },
  })
}

export const useUpdateRadar = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Radar> }) =>
      radarService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['radars'] })
      toast.success('Radar atualizado com sucesso!')
    },
    onError: (error) => {
      toast.error('Erro ao atualizar radar: ' + error.message)
    },
  })
}

export const useDeleteRadar = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: radarService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['radars'] })
      toast.success('Radar excluído com sucesso!')
    },
    onError: (error) => {
      toast.error('Erro ao excluir radar: ' + error.message)
    },
  })
}
3. Hook para Oportunidades


// hooks/useOpportunities.ts
import { useQuery, useInfiniteQuery } from '@tanstack/react-query'
import { opportunityService } from '@/services/opportunityService'

export const useOpportunities = (filters?: any) => {
  return useInfiniteQuery({
    queryKey: ['opportunities', filters],
    queryFn: ({ pageParam = 1 }) =>
      opportunityService.getAll({ ...filters, page: pageParam }),
    getNextPageParam: (lastPage) => lastPage.nextPage,
    initialPageParam: 1,
  })
}

export const useOpportunity = (id: string) => {
  return useQuery({
    queryKey: ['opportunity', id],
    queryFn: () => opportunityService.getById(id),
    enabled: !!id,
  })
}

export const useOpportunityStats = () => {
  return useQuery({
    queryKey: ['opportunity-stats'],
    queryFn: opportunityService.getStats,
    refetchInterval: 5 * 60 * 1000, // 5 minutos
  })
}
4. Hook para Filtros


// hooks/useFilters.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface FilterState {
  selectedRadars: string[]
  urgencyFilter: 'urgent' | 'week' | 'any'
  dateRange: { start: string; end: string }
  searchTerm: string
  setSelectedRadars: (radars: string[]) => void
  setUrgencyFilter: (filter: 'urgent' | 'week' | 'any') => void
  setDateRange: (range: { start: string; end: string }) => void
  setSearchTerm: (term: string) => void
  clearFilters: () => void
}

export const useFilters = create<FilterState>()(
  persist(
    (set) => ({
      selectedRadars: [],
      urgencyFilter: 'any',
      dateRange: { start: '', end: '' },
      searchTerm: '',
      setSelectedRadars: (radars) => set({ selectedRadars: radars }),
      setUrgencyFilter: (filter) => set({ urgencyFilter: filter }),
      setDateRange: (range) => set({ dateRange: range }),
      setSearchTerm: (term) => set({ searchTerm: term }),
      clearFilters: () => set({
        selectedRadars: [],
        urgencyFilter: 'any',
        dateRange: { start: '', end: '' },
        searchTerm: '',
      }),
    }),
    {
      name: 'nradar-filters',
    }
  )
)
Serviços de API

1. Serviço Base


// services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Interceptor para adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para tratar erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export { api }
2. Serviço de Radars


// services/radarService.ts
import { api } from './api'
import { Radar } from '@/types'

export const radarService = {
  async getAll(): Promise<Radar[]> {
    const response = await api.get('/radars')
    return response.data
  },

  async getById(id: string): Promise<Radar> {
    const response = await api.get(`/radars/${id}`)
    return response.data
  },

  async create(data: Omit<Radar, 'id' | 'createdAt' | 'updatedAt'>): Promise<Radar> {
    const response = await api.post('/radars', data)
    return response.data
  },

  async update(id: string, data: Partial<Radar>): Promise<Radar> {
    const response = await api.put(`/radars/${id}`, data)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/radars/${id}`)
  },

  async toggleActive(id: string): Promise<Radar> {
    const response = await api.patch(`/radars/${id}/toggle`)
    return response.data
  },
}
Componentes Principais

1. Layout Principal


// components/layout/Layout.tsx
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import { MobileNavigation } from './MobileNavigation'
import { useAuth } from '@/hooks/useAuth'

export const Layout = () => {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar Desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <Sidebar />
      </div>

      {/* Mobile Navigation */}
      <MobileNavigation />

      {/* Main Content */}
      <div className="lg:pl-72">
        <Header />
        <main className="py-8">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
2. Card de Oportunidade


// components/OpportunityCard.tsx
import { formatCurrency, formatDate } from '@/utils/format'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Opportunity } from '@/types'

interface OpportunityCardProps {
  opportunity: Opportunity
  onViewDetails: (id: string) => void
}

export const OpportunityCard = ({ opportunity, onViewDetails }: OpportunityCardProps) => {
  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'urgent': return 'bg-red-100 text-red-800'
      case 'week': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getUrgencyText = (urgency: string) => {
    switch (urgency) {
      case 'urgent': return 'Urgente'
      case 'week': return 'Próxima Semana'
      default: return 'Normal'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {opportunity.objetoCompra}
          </h3>
          <p className="text-sm text-gray-600 mb-2">
            {opportunity.orgaoEntidade.razaoSocial}
          </p>
          <p className="text-sm text-gray-500">
            {opportunity.unidadeOrgao.municipioNome} - {opportunity.unidadeOrgao.ufSigla}
          </p>
        </div>
        <Badge className={getUrgencyColor(opportunity.urgency)}>
          {getUrgencyText(opportunity.urgency)}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-500">Modalidade</p>
          <p className="font-medium">{opportunity.modalidadeNome}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Valor Estimado</p>
          <p className="font-medium">
            {formatCurrency(opportunity.valorTotalEstimado)}
          </p>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-500">Encerramento</p>
        <p className="font-medium text-orange-600">
          {formatDate(opportunity.dataEncerramentoProposta)}
        </p>
      </div>

      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          size="sm"
          onClick={() => window.open(opportunity.linkSistemaOrigem, '_blank')}
        >
          Ver no Sistema Original
        </Button>
        <Button
          size="sm"
          onClick={() => onViewDetails(opportunity.id)}
        >
          Ver Detalhes
        </Button>
      </div>
    </div>
  )
}
3. Formulário de Radar


// components/forms/RadarForm.tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Checkbox } from '@/components/ui/Checkbox'
import { Switch } from '@/components/ui/Switch'
import { MODALIDADES, CATEGORIAS, ESTADOS } from '@/constants/pncp'

const radarSchema = z.object({
  name: z.string().min(1, 'Nome é obrigatório'),
  keywords: z.array(z.string()).min(1, 'Pelo menos uma palavra-chave é obrigatória'),
  locations: z.object({
    states: z.array(z.string()),
    cities: z.array(z.string()),
  }),
  contractModalities: z.array(z.number()),
  categories: z.array(z.number()),
  urgencyFilter: z.enum(['urgent', 'week', 'any']),
  notifications: z.object({
    email: z.boolean(),
    push: z.boolean(),
  }),
  isActive: z.boolean(),
})

type RadarFormData = z.infer<typeof radarSchema>

interface RadarFormProps {
  initialData?: Partial<RadarFormData>
  onSubmit: (data: RadarFormData) => void
  isLoading?: boolean
}

export const RadarForm = ({ initialData, onSubmit, isLoading }: RadarFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<RadarFormData>({
    resolver: zodResolver(radarSchema),
    defaultValues: initialData,
  })

  const watchedStates = watch('locations.states')

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Nome do Radar */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Nome do Radar
        </label>
        <Input
          {...register('name')}
          placeholder="Ex: Licitações de TI - São Paulo"
          error={errors.name?.message}
        />
      </div>

      {/* Palavras-chave */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Palavras-chave
        </label>
        <Input
          placeholder="Digite as palavras-chave separadas por vírgula"
          onChange={(e) => {
            const keywords = e.target.value.split(',').map(k => k.trim()).filter(Boolean)
            setValue('keywords', keywords)
          }}
          error={errors.keywords?.message}
        />
      </div>

      {/* Localização */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Estados
          </label>
          <Select
            multiple
            options={ESTADOS}
            {...register('locations.states')}
            error={errors.locations?.states?.message}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Municípios
          </label>
          <Select
            multiple
            options={[]} // Carregar baseado nos estados selecionados
            {...register('locations.cities')}
            disabled={!watchedStates?.length}
            error={errors.locations?.cities?.message}
          />
        </div>
      </div>

      {/* Modalidades */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Modalidades de Contratação
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {MODALIDADES.map((modalidade) => (
            <Checkbox
              key={modalidade.codigo}
              label={modalidade.nome}
              {...register('contractModalities')}
              value={modalidade.codigo}
            />
          ))}
        </div>
      </div>

      {/* Categorias */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Categorias
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {CATEGORIAS.map((categoria) => (
            <Checkbox
              key={categoria.codigo}
              label={categoria.nome}
              {...register('categories')}
              value={categoria.codigo}
            />
          ))}
        </div>
      </div>

      {/* Filtro de Urgência */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Filtro de Urgência
        </label>
        <Select
          options={[
            { value: 'urgent', label: 'Urgente (3 dias)' },
            { value: 'week', label: 'Próxima Semana (7 dias)' },
            { value: 'any', label: 'Qualquer Prazo' },
          ]}
          {...register('urgencyFilter')}
          error={errors.urgencyFilter?.message}
        />
      </div>

      {/* Notificações */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Notificações
        </label>
        <div className="space-y-3">
          <Switch
            label="Notificações por E-mail"
            {...register('notifications.email')}
          />
          <Switch
            label="Notificações Push"
            {...register('notifications.push')}
          />
        </div>
      </div>

      {/* Status */}
      <div>
        <Switch
          label="Radar Ativo"
          {...register('isActive')}
        />
      </div>

      {/* Botões */}
      <div className="flex justify-end space-x-4">
        <Button type="button" variant="outline">
          Cancelar
        </Button>
        <Button type="submit" loading={isLoading}>
          Salvar Radar
        </Button>
      </div>
    </form>
  )
}
Páginas Principais

1. Dashboard


// pages/Dashboard.tsx
import { useOpportunityStats } from '@/hooks/useOpportunities'
import { useRadars } from '@/hooks/useRadars'
import { StatsCard } from '@/components/StatsCard'
import { Chart } from '@/components/Chart'
import { RecentOpportunities } from '@/components/RecentOpportunities'

export const Dashboard = () => {
  const { data: stats, isLoading: statsLoading } = useOpportunityStats()
  const { data: radars, isLoading: radarsLoading } = useRadars()

  if (statsLoading || radarsLoading) {
    return <div>Carregando...</div>
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">
          Visão geral das suas oportunidades e radares
        </p>
      </div>

      {/* Cards de Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Oportunidades Ativas"
          value={stats?.activeOpportunities || 0}
          icon="📊"
          trend={{ value: 12, direction: 'up' }}
        />
        <StatsCard
          title="Radares Ativos"
          value={radars?.filter(r => r.isActive).length || 0}
          icon="🎯"
        />
        <StatsCard
          title="Valor Total"
          value={`R$ ${(stats?.totalValue || 0).toLocaleString()}`}
          icon="💰"
          trend={{ value: 8, direction: 'up' }}
        />
        <StatsCard
          title="Urgentes"
          value={stats?.urgentOpportunities || 0}
          icon="⚡"
          color="red"
        />
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Chart
          title="Oportunidades por Modalidade"
          type="pie"
          data={stats?.modalityChart || []}
        />
        <Chart
          title="Tendência Mensal"
          type="line"
          data={stats?.monthlyTrend || []}
        />
      </div>

      {/* Oportunidades Recentes */}
      <RecentOpportunities />
    </div>
  )
}
2. Feed de Oportunidades


// pages/Feed.tsx
import { useState } from 'react'
import { useOpportunities } from '@/hooks/useOpportunities'
import { useFilters } from '@/hooks/useFilters'
import { OpportunityCard } from '@/components/OpportunityCard'
import { FilterSidebar } from '@/components/FilterSidebar'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'

export const Feed = () => {
  const [filtersOpen, setFiltersOpen] = useState(false)
  const filters = useFilters()
  
  const {
    data,
    isLoading,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useOpportunities(filters)

  const opportunities = data?.pages.flatMap(page => page.data) || []

  return (
    <div className="flex">
      {/* Sidebar de Filtros */}
      <FilterSidebar
        open={filtersOpen}
        onClose={() => setFiltersOpen(false)}
      />

      {/* Conteúdo Principal */}
      <div className="flex-1">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Feed de Oportunidades
          </h1>
          <button
            onClick={() => setFiltersOpen(true)}
            className="lg:hidden px-4 py-2 bg-blue-600 text-white rounded-md"
          >
            Filtros
          </button>
        </div>

        {/* Lista de Oportunidades */}
        {isLoading ? (
          <LoadingSpinner />
        ) : opportunities.length === 0 ? (
          <EmptyState
            title="Nenhuma oportunidade encontrada"
            description="Tente ajustar seus filtros ou criar um novo radar"
          />
        ) : (
          <div className="space-y-4">
            {opportunities.map((opportunity) => (
              <OpportunityCard
                key={opportunity.id}
                opportunity={opportunity}
                onViewDetails={(id) => navigate(`/opportunity/${id}`)}
              />
            ))}

            {/* Carregamento de mais itens */}
            {hasNextPage && (
              <div className="text-center py-4">
                <button
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                  className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  {isFetchingNextPage ? 'Car


Copy Answer

Share

Get more from this answer

Translate

Regenerate

Claude 4 Sonnet Thinking
Prompt Suggestions:
Detalhe a implementação do ProtectedRoute e sua integração com a autenticação JWT.
Explique estratégias de caching e invalidação para dados críticos usando React Query.
Descreva a abordagem para internacionalização e suporte a múltiplos idiomas no nRadar.

G
Detalhe um projeto frontend completo para o sistema nRadar, especificando a estrutura de rotas, hooks personalizados para gerenciamento de estado e chamadas de API, além das melhores práticas para organização de componentes e integração com back-end. Forneça um plano de arquitetura que inclua rotas principais e aninhadas, estratégias de carregamento de dados, uso de bibliotecas recomendadas (como React Router, React Query ou Context API), e exemplos de código para os hooks que atendam às funcionalidades do nRadar. Inclua também instruções para configuração inicial, integração de estilos e responsividade para um produto final robusto e escalável.



Reasoning


Copy Answer

Share

Get more from this answer

Translate

Regenerate

O3
Prompt Suggestions:
Detalhe a estrutura de rotas aninhadas para gerenciar diferentes níveis de navegação no nRadar Frontend
Explique o funcionamento e uso do hook useOpportunities com filtros avançados para chamadas API
Descreva a estratégia para autenticação e autorização usando Context API ou bibliotecas de terceiros

G
Descreva detalhadamente a implementação do componente ProtectedRoute em uma aplicação React, incluindo como ele verifica a autenticação do usuário utilizando tokens JWT e como essa verificação é integrada ao fluxo de autenticação. Explique também as melhores práticas para gerenciamento seguro desses tokens no cliente, incluindo armazenamento e renovação. Além disso, detalhe estratégias eficazes de caching e invalidação de dados críticos utilizando React Query, destacando como garantir a consistência dos dados e a performance da aplicação, com exemplos de configurações recomendadas para queries e mutações. Por fim, apresente a abordagem adotada no nRadar para internacionalização, incluindo o suporte a múltiplos idiomas, as bibliotecas ou frameworks utilizados, a gestão de arquivos de tradução, e como garantir a adaptação dinâmica do conteúdo conforme o idioma selecionado pelo usuário.



Reasoning

Answer
1 – Componente ProtectedRoute


// src/components/ProtectedRoute.tsx
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'

export const ProtectedRoute = () => {
  const { isAuthenticated, isTokenExpired } = useAuth()
  const location = useLocation()

  if (!isAuthenticated || isTokenExpired) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return <Outlet />           // renderiza children se passou
}
Fluxo de autenticação e verificação do JWT

Login → /auth/login devolve accessToken (vida curta) + refreshToken (vida longa).
AuthContext guarda:

const [accessToken, setAccessToken] = useState<string | null>(null)
const [refreshToken, setRefreshToken] = useState<string | null>(null)

const isAuthenticated  = !!accessToken
const isTokenExpired   = useMemo(() => {
  if (!accessToken) return true
  const { exp } = jwtDecode<{ exp:number }>(accessToken)
  return Date.now() >= exp * 1000
}, [accessToken])
Um axios interceptor captura respostas 401, chama /auth/refresh, atualiza o contexto e repete a request falhada:

api.interceptors.response.use(
  r => r,
  async error => {
    if (error.response?.status === 401 && refreshToken) {
      const { data } = await api.post('/auth/refresh', { refreshToken })
      setAccessToken(data.accessToken)
      error.config.headers.Authorization = `Bearer ${data.accessToken}`
      return api.request(error.config)
    }
    return Promise.reject(error)
  }
)
ProtectedRoute consulta apenas o estado global; se o token estiver expirado forçará AuthContext a tentar renovar (ex.: via useEffect) ou redirecionará ao login.

2 – Boas práticas para guardar e renovar tokens

Item	Melhor abordagem em SPA
Download as CSV
Download as CSV


Copy Answer

Share

Get more from this answer

Translate

Regenerate


G
Descreva detalhadamente a implementação do componente ProtectedRoute em uma aplicação React, incluindo como ele verifica a autenticação do usuário utilizando tokens JWT e como essa verificação é integrada ao fluxo de autenticação. Explique também as melhores práticas para gerenciamento seguro desses tokens no cliente, incluindo armazenamento e renovação. Além disso, detalhe estratégias eficazes de caching e invalidação de dados críticos utilizando React Query, destacando como garantir a consistência dos dados e a performance da aplicação, com exemplos de configurações recomendadas para queries e mutações. Por fim, apresente a abordagem adotada no nRadar para internacionalização, incluindo o suporte a múltiplos idiomas, as bibliotecas ou frameworks utilizados, a gestão de arquivos de tradução, e como garantir a adaptação dinâmica do conteúdo conforme o idioma selecionado pelo usuário.



Reasoning

Answer
Projeto Frontend Completo - Sistema nRadar

1. Estrutura de Projeto e Configuração Inicial

Stack Tecnológica Recomendada


{
  "framework": "React 18 + TypeScript",
  "routing": "React Router DOM v6",
  "state": "Zustand + React Query v4",
  "styling": "Tailwind CSS + Headless UI",
  "forms": "React Hook Form + Zod",
  "i18n": "react-i18next",
  "build": "Vite",
  "testing": "Vitest + Testing Library"
}
Estrutura de Pastas


src/
├── components/           # Componentes reutilizáveis
│   ├── ui/              # Componentes base (Button, Input, etc.)
│   ├── forms/           # Componentes de formulário
│   └── layout/          # Componentes de layout
├── pages/               # Páginas da aplicação
├── hooks/               # Hooks customizados
├── services/            # Serviços de API
├── stores/              # Stores Zustand
├── utils/               # Utilitários e helpers
├── types/               # Definições TypeScript
├── constants/           # Constantes da aplicação
└── locales/             # Arquivos de tradução
2. Implementação do ProtectedRoute

Componente ProtectedRoute


// components/ProtectedRoute.tsx
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

interface ProtectedRouteProps {
  requiredRole?: string[]
  fallback?: React.ReactNode
}

export const ProtectedRoute = ({ 
  requiredRole = [], 
  fallback = <LoadingSpinner /> 
}: ProtectedRouteProps) => {
  const { user, isAuthenticated, isLoading, hasRole } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return fallback
  }

  if (!isAuthenticated) {
    return (
      <Navigate 
        to="/login" 
        replace 
        state={{ from: location }} 
      />
    )
  }

  if (requiredRole.length > 0 && !hasRole(requiredRole)) {
    return <Navigate to="/unauthorized" replace />
  }

  return <Outlet />
}
```

## Exemplo de Interceptor Axios para Token JWT

```ts
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

---

*Data de organização: 6 de julho de 2025*
