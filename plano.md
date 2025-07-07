# Plano Detalhado: Plataforma nRadar (MVP Refinado)

A nRadar será uma plataforma de inteligência de mercado e alertas que conecta fornecedores a oportunidades de licitação, monitorando continuamente o Portal Nacional de Contratações Públicas (PNCP) via API.

## 1. Onboarding e Cadastro do Usuário

O objetivo desta etapa é oferecer um processo de entrada rápido e descomplicado para que o usuário possa começar a configurar seus interesses o mais breve possível.

### Cadastro Padrão
- Manter a funcionalidade de cadastro via e-mail e senha
- Verificação de e-mail para garantir a validade do contato

### Login Social
- Implementar login com provedores populares como Google e LinkedIn
- Reduz a fricção, agiliza o acesso e aumenta a taxa de conversão de cadastros

### Perfil Básico
- Após o primeiro login, o usuário preencherá informações básicas:
  - Nome da empresa
  - CNPJ
  - Área de atuação principal
- Informações podem ser usadas para sugerir configurações de radar iniciais

## 2. Criação e Gerenciamento de Perfis de Interesse (Radar)

Esta é a funcionalidade central da plataforma. Um "Radar" é um conjunto de filtros salvos que busca ativamente por novas oportunidades. O usuário poderá criar múltiplos radares para diferentes estratégias de negócio.

### Campos de Configuração do Perfil (Radar):

#### Nome do Perfil
- Campo de texto para identificar facilmente cada radar
- Exemplos: "Licitações de TI - São Paulo", "Serviços de Engenharia - Nordeste"

#### Palavras-chave
- Campo de texto para inserir termos que serão buscados no objeto da contratação
- Utiliza campos `objetoCompra` e `informacaoComplementar`

#### Localização
- **Estado (UF)**: Seletor múltiplo para escolher um ou mais estados de interesse
  - Utiliza parâmetro `uf` da API
- **Município**: Seletor múltiplo que permite pesquisar e adicionar municípios
  - Utiliza parâmetro `codigoMunicipioIbge`

#### Modalidades de Contratação
Lista de checkboxes baseada na tabela de domínio "Modalidade de Contratação" (Seção 5.2 do manual):
- Leilão (Eletrônico/Presencial)
- Diálogo Competitivo
- Concurso
- Concorrência (Eletrônica/Presencial)
- Pregão (Eletrônico/Presencial)
- Dispensa de Licitação
- Inexigibilidade
- Credenciamento

#### Categorias do Produto/Serviço
Lista de checkboxes baseada na tabela "Categoria do Processo" (Seção 5.11 do manual):
- Compras
- Informática (TIC)
- Obras
- Serviços de Engenharia
- Serviços de Saúde
- Mão de Obra
- Locação Imóveis

#### Filtro de Urgência
Seletor de opção única baseado no campo `dataEncerramentoProposta`:
- **Urgente**: Oportunidades que encerram em até 3 dias
- **Próxima Semana**: Oportunidades que encerram em até 7 dias
- **Qualquer Prazo**: Exibir todas as oportunidades, independentemente do prazo

## 3. Configuração de Notificações

Para garantir que os usuários não percam nenhuma oportunidade, o sistema de notificação deve ser flexível e personalizável para cada radar criado.

### Canais de Notificação
Para cada radar, o usuário poderá habilitar ou desabilitar independentemente:

#### Notificações por E-mail
- Resumo diário ou alertas instantâneos com as novas oportunidades encontradas

#### Notificações Push (Mobile)
- Alertas em tempo real enviados para o aplicativo móvel da nRadar

### Gerenciamento Centralizado
- Tela de "Configurações de Notificação" para visualizar e ajustar as preferências de todos os radares em um único lugar

## 4. Sistema de Feed de Oportunidades

O feed é a tela principal onde os resultados dos radares ativos são exibidos de forma clara e organizada.

### Visualização Agregada
- Feed principal exibirá uma lista cronológica de todas as oportunidades que correspondem a qualquer um dos radares ativos do usuário

### Filtragem por Radar
- O usuário poderá filtrar o feed para visualizar oportunidades de um radar específico

### Card Resumido da Oportunidade
Cada oportunidade será exibida em um card contendo informações essenciais extraídas da API:
- **Objeto da Contratação**: `objetoCompra`
- **Órgão/Entidade**: `orgaoEntidade.razaosocial`
- **Localização**: `unidadeOrgao.municipioNome - unidadeOrgao.ufSigla`
- **Modalidade**: `modalidadeNome`
- **Data de Encerramento**: `dataEncerramentoProposta`, com selo visual de urgência ("Urgente", "Encerra Hoje")

## 5. Tela de Detalhes da Oportunidade

Ao clicar em um card, o usuário acessará uma página com todas as informações disponíveis sobre a licitação, extraídas diretamente da API do PNCP para garantir a precisão.

### Informações Completas
A tela exibirá todos os dados relevantes retornados pelo serviço "Consultar Contratações com Período de Recebimento de Propostas em Aberto":

#### Identificação
- Nº do Controle PNCP (`numeroControlePNCP`)
- Nº da Compra (`numeroCompra`)
- Processo (`processo`)

#### Descrição
- Objeto completo (`objetoCompra`)
- Informações Complementares (`informacaoComplementar`)

#### Datas e Prazos
- Data de Abertura (`dataAberturaProposta`)
- Data de Encerramento (`dataEncerramentoProposta`)

#### Valores
- Valor Total Estimado (`valorTotalEstimado`)

#### Dados do Órgão
- Razão Social (`orgaoEntidade.razaosocial`)
- CNPJ
- Unidade (`unidadeOrgao.nomeUnidade`)

#### Link Direto
- Botão de destaque com o `linkSistemaOrigem` para que o usuário possa acessar a página original da licitação, onde poderá obter os editais e enviar sua proposta

## Recomendações para Otimização de Usabilidade e Precisão

Para diferenciar a nRadar e entregar uma experiência superior, considere as seguintes otimizações:

### Melhorar a Precisão dos Filtros

#### Busca Avançada
- Permita o uso de operadores booleanos nas palavras-chave
- Exemplo: `desenvolvimento E "aplicativo móvel" NÃO manutenção`

#### Aproveitar Filtros Adicionais da API
- Incorpore filtros para `srp` (Sistema de Registro de Preços)
- Filtros para `tipoInstrumentoConvocatorioNome` (Edital, Aviso de Contratação Direta, etc.)
- Campos disponíveis na API que podem ser cruciais para certos nichos de mercado

### Otimizar a Usabilidade

#### Onboarding Guiado
- Crie um "wizard" passo a passo que ajude o novo usuário a configurar seu primeiro radar
- Explique cada campo durante o processo

#### Templates de Radar
- Ofereça perfis pré-configurados para setores comuns:
  - "Construção Civil"
  - "Material de Escritório"
  - "Software como Serviço"
- Usuários podem ativar e personalizar esses templates

#### Feedback nas Oportunidades
- Permita que os usuários marquem uma oportunidade como "Relevante" ou "Não relevante"
- Use essa informação para sugerir melhorias nos filtros do radar
- Futuramente, pode treinar um modelo de recomendação

## Visão de Futuro (Além do MVP)

### Inteligência de Longo Prazo com PCA
- Para uma vantagem estratégica, desenvolva uma funcionalidade que monitore o Plano de Contratações Anual (PCA)
- Use os serviços 6.1 e 6.2 do manual
- Permitirá que usuários se antecipem às futuras licitações, preparando-se com meses de antecedência

### Análise de Concorrência
- Analise dados de licitações passadas e atas de registro de preços (Serviço 6.5)
- Forneça insights sobre quais empresas estão vencendo licitações em determinados segmentos
- Analise a que preços estão sendo fechados os contratos

## Conclusão

A implementação deste plano permitirá que a nRadar se posicione como uma ferramenta indispensável, transformando o vasto volume de dados do PNCP em inteligência acionável e oportunidades de negócio concretas para seus usuários.

---

*Data de criação: 6 de julho de 2025*
*Baseado no Manual das APIs de Consultas do PNCP*
