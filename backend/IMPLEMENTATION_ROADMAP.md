# Roadmap de Implementação - SEARCB Backend

## Visão Geral

Este documento detalha os componentes que foram identificados como removidos ou não implementados durante a auditoria da documentação da API SEARCB. O objetivo é fornecer um guia completo para implementar essas funcionalidades faltantes.

## Componentes Não Implementados

### 1. Webhooks Internos

#### 1.1 Endpoint de Notificação Interna

**Endpoint**: `POST /webhooks/interno/notification`

**Finalidade**: Receber notificações internas do sistema (alertas, eventos de negócio, etc.)

**Implementação Necessária**:

```python
# app/api/endpoints/webhooks.py

@router.post("/interno/notification")
@limiter.limit("50/minute")
async def receber_notificacao_interna(
    request: Request,
    payload: NotificacaoInternaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Recebe notificações internas do sistema
    
    Tipos de notificação suportados:
    - contrato_vencendo: Contrato próximo ao vencimento
    - pca_atualizado: PCA foi atualizado
    - erro_sincronizacao: Erro na sincronização com PNCP
    - limite_orcamento: Limite orçamentário atingido
    """
    
    try:
        # Validar tipo de notificação
        if payload.tipo not in ["contrato_vencendo", "pca_atualizado", "erro_sincronizacao", "limite_orcamento"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de notificação inválido"
            )
        
        # Processar notificação de acordo com o tipo
        if payload.tipo == "contrato_vencendo":
            await processar_contrato_vencendo(payload.dados, db)
        elif payload.tipo == "pca_atualizado":
            await processar_pca_atualizado(payload.dados, db)
        elif payload.tipo == "erro_sincronizacao":
            await processar_erro_sincronizacao(payload.dados, db)
        elif payload.tipo == "limite_orcamento":
            await processar_limite_orcamento(payload.dados, db)
        
        # Registrar evento no log
        logger.info(f"Notificação interna processada: {payload.tipo}")
        
        return {
            "status": "success",
            "message": "Notificação processada com sucesso",
            "tipo": payload.tipo,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar notificação interna: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar notificação"
        )
```

**Schemas Necessários**:

```python
# app/schemas/webhooks.py

class NotificacaoInternaRequest(BaseModel):
    tipo: str = Field(..., description="Tipo de notificação")
    dados: Dict[str, Any] = Field(..., description="Dados da notificação")
    origem: str = Field(..., description="Sistema/módulo de origem")
    prioridade: str = Field("normal", description="Prioridade da notificação")
    
    class Config:
        schema_extra = {
            "example": {
                "tipo": "contrato_vencendo",
                "dados": {
                    "contrato_id": 123,
                    "numero_contrato": "CT-2024-001",
                    "dias_vencimento": 30
                },
                "origem": "sistema_monitoramento",
                "prioridade": "alta"
            }
        }

class NotificacaoInternaResponse(BaseModel):
    status: str
    message: str
    tipo: str
    timestamp: str
```

### 2. Endpoints de Administração

#### 2.1 Endpoint de Logs do Sistema

**Endpoint**: `GET /admin/logs`

**Implementação Necessária**:

```python
# app/api/endpoints/admin.py

@router.get("/logs")
@limiter.limit("50/minute")
async def listar_logs(
    request,
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(50, ge=1, le=200, description="Tamanho da página"),
    nivel: Optional[str] = Query(None, description="Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)"),
    modulo: Optional[str] = Query(None, description="Módulo/arquivo de origem"),
    data_inicio: Optional[date] = Query(None, description="Data de início (YYYY-MM-DD)"),
    data_fim: Optional[date] = Query(None, description="Data de fim (YYYY-MM-DD)"),
    termo_busca: Optional[str] = Query(None, description="Termo de busca na mensagem"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista logs do sistema com filtros e paginação
    
    Requer permissão de administrador
    """
    
    # Verificar permissões
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Construir query base
    query = db.query(LogSistema)
    
    # Aplicar filtros
    if nivel:
        query = query.filter(LogSistema.nivel == nivel.upper())
    
    if modulo:
        query = query.filter(LogSistema.modulo.ilike(f"%{modulo}%"))
    
    if data_inicio:
        query = query.filter(LogSistema.timestamp >= data_inicio)
    
    if data_fim:
        query = query.filter(LogSistema.timestamp <= data_fim)
    
    if termo_busca:
        query = query.filter(LogSistema.mensagem.ilike(f"%{termo_busca}%"))
    
    # Ordenar por timestamp decrescente
    query = query.order_by(LogSistema.timestamp.desc())
    
    # Paginar
    result = paginate_query(query, page, size)
    
    return result
```

#### 2.2 Endpoints de Configurações do Sistema

**Endpoints**: 
- `GET /admin/configuracoes`
- `PUT /admin/configuracoes/{chave}`

**Implementação Necessária**:

```python
# app/api/endpoints/admin.py

@router.get("/configuracoes")
@limiter.limit("100/minute")
async def listar_configuracoes(
    request,
    categoria: Optional[str] = Query(None, description="Categoria das configurações"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista configurações do sistema
    
    Requer permissão de administrador
    """
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Verificar cache
    cache_key = f"configuracoes_{categoria or 'all'}"
    cached_result = await get_cache(cache_key)
    if cached_result:
        return cached_result
    
    # Construir query
    query = db.query(ConfiguracaoSistema)
    
    if categoria:
        query = query.filter(ConfiguracaoSistema.categoria == categoria)
    
    configuracoes = query.all()
    
    # Agrupar por categoria
    result = {}
    for config in configuracoes:
        if config.categoria not in result:
            result[config.categoria] = []
        
        result[config.categoria].append({
            "chave": config.chave,
            "valor": config.valor,
            "descricao": config.descricao,
            "tipo": config.tipo,
            "editavel": config.editavel,
            "ultima_atualizacao": config.updated_at
        })
    
    # Cache por 1 hora
    await set_cache(cache_key, result, expire=3600)
    
    return result

@router.put("/configuracoes/{chave}")
@limiter.limit("10/minute")
async def atualizar_configuracao(
    chave: str,
    request: AtualizarConfiguracaoRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza configuração específica
    
    Requer permissão de administrador
    """
    
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    # Buscar configuração
    config = db.query(ConfiguracaoSistema).filter(
        ConfiguracaoSistema.chave == chave
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuração não encontrada"
        )
    
    if not config.editavel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta configuração não pode ser editada"
        )
    
    # Validar tipo do valor
    if not validar_tipo_configuracao(request.valor, config.tipo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Valor inválido para o tipo {config.tipo}"
        )
    
    # Atualizar configuração
    config.valor = request.valor
    config.updated_at = datetime.now()
    
    db.commit()
    
    # Invalidar cache
    await delete_cache_pattern("configuracoes_*")
    
    # Log da alteração
    logger.info(f"Configuração {chave} atualizada por {current_user.username}")
    
    return {
        "status": "success",
        "message": "Configuração atualizada com sucesso",
        "chave": chave,
        "valor": request.valor
    }
```

### 3. Endpoints de Perfil de Usuário

#### 3.1 Endpoints de Perfil

**Endpoints**:
- `GET /usuarios/me/profile`
- `PUT /usuarios/me/profile`
- `POST /usuarios/{id}/change-password`

**Implementação Necessária**:

```python
# app/api/endpoints/usuarios.py

@router.get("/me/profile", response_model=PerfilUsuarioResponse)
@limiter.limit("100/minute")
async def obter_perfil_atual(
    request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtém perfil do usuário atual
    """
    
    perfil = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "nome_completo": current_user.nome_completo,
        "telefone": current_user.telefone,
        "cargo": current_user.cargo,
        "orgao_cnpj": current_user.orgao_cnpj,
        "orgao_nome": current_user.orgao_nome,
        "is_admin": current_user.is_admin,
        "is_gestor": current_user.is_gestor,
        "is_operador": current_user.is_operador,
        "ativo": current_user.ativo,
        "ultimo_login": current_user.ultimo_login,
        "data_criacao": current_user.created_at,
        "configuracoes": current_user.configuracoes or {}
    }
    
    return perfil

@router.put("/me/profile", response_model=PerfilUsuarioResponse)
@limiter.limit("20/minute")
async def atualizar_perfil_atual(
    request: AtualizarPerfilRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atualiza perfil do usuário atual
    """
    
    # Campos que o usuário pode atualizar
    campos_permitidos = ["nome_completo", "telefone", "cargo", "configuracoes"]
    
    for campo in campos_permitidos:
        if hasattr(request, campo) and getattr(request, campo) is not None:
            setattr(current_user, campo, getattr(request, campo))
    
    current_user.updated_at = datetime.now()
    
    try:
        db.commit()
        
        logger.info(f"Perfil atualizado pelo usuário {current_user.username}")
        
        return await obter_perfil_atual(None, current_user, db)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar perfil: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar perfil"
        )

@router.post("/{usuario_id}/change-password")
@limiter.limit("5/minute")
async def alterar_senha_usuario(
    usuario_id: int,
    request: AlterarSenhaRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Altera senha de usuário
    
    Administradores podem alterar senha de qualquer usuário
    Usuários comuns só podem alterar a própria senha
    """
    
    # Verificar permissões
    if usuario_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para alterar senha deste usuário"
        )
    
    # Buscar usuário
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar senha atual (apenas para o próprio usuário)
    if usuario_id == current_user.id:
        if not security_service.verify_password(request.senha_atual, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Senha atual incorreta"
            )
    
    # Validar nova senha
    if len(request.nova_senha) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha deve ter pelo menos 8 caracteres"
        )
    
    # Atualizar senha
    usuario.senha_hash = security_service.get_password_hash(request.nova_senha)
    usuario.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"Senha alterada para usuário {usuario.username}")
    
    return {
        "status": "success",
        "message": "Senha alterada com sucesso"
    }
```

### 4. Modelos de Dados Necessários

#### 4.1 Modelo de Log do Sistema

```python
# app/models/log_sistema.py

class LogSistema(BaseModel):
    __tablename__ = "log_sistema"
    
    nivel = Column(String(10), index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    modulo = Column(String(100), index=True)
    mensagem = Column(Text)
    timestamp = Column(DateTime, default=func.now(), index=True)
    user_id = Column(Integer, ForeignKey("usuario.id"), nullable=True)
    request_id = Column(String(50), nullable=True)
    detalhes = Column(JSON, nullable=True)
    
    # Relacionamento
    usuario = relationship("Usuario", backref="logs")
```

#### 4.2 Modelo de Configuração do Sistema

```python
# app/models/configuracao_sistema.py

class ConfiguracaoSistema(BaseModel):
    __tablename__ = "configuracao_sistema"
    
    chave = Column(String(100), unique=True, index=True)
    valor = Column(Text)
    descricao = Column(Text)
    categoria = Column(String(50), index=True)
    tipo = Column(String(20))  # string, integer, boolean, json
    editavel = Column(Boolean, default=True)
    valor_padrao = Column(Text)
```

### 5. Schemas Necessários

```python
# app/schemas/admin.py

class LogSistemaResponse(BaseModel):
    id: int
    nivel: str
    modulo: str
    mensagem: str
    timestamp: datetime
    user_id: Optional[int]
    request_id: Optional[str]
    detalhes: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class ConfiguracaoSistemaResponse(BaseModel):
    chave: str
    valor: str
    descricao: str
    categoria: str
    tipo: str
    editavel: bool
    ultima_atualizacao: datetime
    
    class Config:
        from_attributes = True

class AtualizarConfiguracaoRequest(BaseModel):
    valor: str = Field(..., description="Novo valor da configuração")

# app/schemas/usuario.py

class PerfilUsuarioResponse(BaseModel):
    id: int
    username: str
    email: str
    nome_completo: str
    telefone: Optional[str]
    cargo: Optional[str]
    orgao_cnpj: Optional[str]
    orgao_nome: Optional[str]
    is_admin: bool
    is_gestor: bool
    is_operador: bool
    ativo: bool
    ultimo_login: Optional[datetime]
    data_criacao: datetime
    configuracoes: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class AtualizarPerfilRequest(BaseModel):
    nome_completo: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    cargo: Optional[str] = Field(None, max_length=100)
    configuracoes: Optional[Dict[str, Any]] = None

class AlterarSenhaRequest(BaseModel):
    senha_atual: Optional[str] = Field(None, description="Senha atual (obrigatória para próprio usuário)")
    nova_senha: str = Field(..., min_length=8, description="Nova senha")
```

### 6. Migrações de Banco de Dados

```python
# migrations/versions/add_logs_and_configs.py

def upgrade():
    # Criar tabela de logs
    op.create_table(
        'log_sistema',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nivel', sa.String(10), nullable=False),
        sa.Column('modulo', sa.String(100), nullable=False),
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('request_id', sa.String(50), nullable=True),
        sa.Column('detalhes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['usuario.id'])
    )
    
    # Criar índices
    op.create_index('ix_log_sistema_nivel', 'log_sistema', ['nivel'])
    op.create_index('ix_log_sistema_modulo', 'log_sistema', ['modulo'])
    op.create_index('ix_log_sistema_timestamp', 'log_sistema', ['timestamp'])
    
    # Criar tabela de configurações
    op.create_table(
        'configuracao_sistema',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chave', sa.String(100), nullable=False, unique=True),
        sa.Column('valor', sa.Text(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('categoria', sa.String(50), nullable=False),
        sa.Column('tipo', sa.String(20), nullable=False),
        sa.Column('editavel', sa.Boolean(), default=True),
        sa.Column('valor_padrao', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Criar índices
    op.create_index('ix_configuracao_sistema_chave', 'configuracao_sistema', ['chave'])
    op.create_index('ix_configuracao_sistema_categoria', 'configuracao_sistema', ['categoria'])
    
    # Inserir configurações padrão
    op.execute("""
        INSERT INTO configuracao_sistema (chave, valor, descricao, categoria, tipo, editavel, valor_padrao, created_at, updated_at)
        VALUES 
        ('pncp_sync_interval', '3600', 'Intervalo de sincronização com PNCP (segundos)', 'integracao', 'integer', true, '3600', NOW(), NOW()),
        ('max_page_size', '500', 'Tamanho máximo de página para consultas', 'api', 'integer', true, '500', NOW(), NOW()),
        ('cache_ttl', '3600', 'Tempo de vida do cache (segundos)', 'cache', 'integer', true, '3600', NOW(), NOW()),
        ('rate_limit_requests', '100', 'Limite de requisições por minuto', 'seguranca', 'integer', true, '100', NOW(), NOW()),
        ('email_notifications', 'true', 'Habilitar notificações por email', 'notificacoes', 'boolean', true, 'true', NOW(), NOW())
    """)
```

### 7. Testes Unitários

```python
# tests/test_webhooks.py

class TestWebhooksInternos:
    
    def test_notificacao_contrato_vencendo(self, client, db_session, admin_user):
        """Teste de notificação de contrato vencendo"""
        payload = {
            "tipo": "contrato_vencendo",
            "dados": {
                "contrato_id": 1,
                "numero_contrato": "CT-2024-001",
                "dias_vencimento": 30
            },
            "origem": "sistema_monitoramento",
            "prioridade": "alta"
        }
        
        response = client.post(
            "/api/v1/webhooks/interno/notification",
            json=payload,
            headers={"Authorization": f"Bearer {admin_user.token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["tipo"] == "contrato_vencendo"

# tests/test_admin.py

class TestAdminEndpoints:
    
    def test_listar_logs(self, client, db_session, admin_user):
        """Teste de listagem de logs"""
        response = client.get(
            "/api/v1/admin/logs",
            headers={"Authorization": f"Bearer {admin_user.token}"}
        )
        
        assert response.status_code == 200
        assert "data" in response.json()
    
    def test_listar_configuracoes(self, client, db_session, admin_user):
        """Teste de listagem de configurações"""
        response = client.get(
            "/api/v1/admin/configuracoes",
            headers={"Authorization": f"Bearer {admin_user.token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
```

## Cronograma de Implementação

### Fase 1 - Funcionalidades Básicas (Semana 1-2)
- [ ] Modelos de dados (LogSistema, ConfiguracaoSistema)
- [ ] Migrações de banco de dados
- [ ] Schemas básicos

### Fase 2 - Endpoints de Administração (Semana 3-4)
- [ ] Endpoint de logs (`GET /admin/logs`)
- [ ] Endpoints de configurações (`GET /admin/configuracoes`, `PUT /admin/configuracoes/{chave}`)
- [ ] Validações e permissões

### Fase 3 - Webhooks Internos (Semana 5-6)
- [ ] Endpoint de notificação interna (`POST /webhooks/interno/notification`)
- [ ] Processadores de notificação por tipo
- [ ] Integração com sistema de logging

### Fase 4 - Perfil de Usuário (Semana 7-8)
- [ ] Endpoints de perfil (`GET /usuarios/me/profile`, `PUT /usuarios/me/profile`)
- [ ] Endpoint de alteração de senha (`POST /usuarios/{id}/change-password`)
- [ ] Validações de segurança

### Fase 5 - Testes e Documentação (Semana 9-10)
- [ ] Testes unitários para todos os endpoints
- [ ] Testes de integração
- [ ] Atualização da documentação OpenAPI
- [ ] Revisão de segurança

## Considerações de Segurança

1. **Autenticação**: Todos os endpoints devem validar tokens JWT
2. **Autorização**: Verificar permissões específicas (admin, gestor, operador)
3. **Rate Limiting**: Aplicar limites apropriados para cada endpoint
4. **Validação de Entrada**: Validar todos os dados de entrada
5. **Logging de Segurança**: Registrar todas as operações sensíveis
6. **Sanitização**: Sanitizar dados antes de salvar no banco

## Monitoramento e Métricas

1. **Logs Estruturados**: Implementar logging estruturado para facilitar análise
2. **Métricas de Performance**: Monitorar tempo de resposta dos endpoints
3. **Alertas**: Configurar alertas para falhas críticas
4. **Dashboards**: Criar dashboards para visualização das métricas

## Conclusão

Este roadmap fornece uma base sólida para implementar os componentes faltantes no sistema SEARCB. A implementação deve seguir as melhores práticas de segurança, performance e manutenibilidade, garantindo que o sistema seja robusto e escalável.
