#!/bin/bash

# Health Check Script for SEARCB Backend
# Checks for common issues and provides prevention recommendations

echo "=== SEARCB Backend Health Check ==="
echo "Executado em: $(date)"
echo ""

# Function to check if service is responding
check_service() {
    echo "1. Verificando se o serviço está respondendo..."
    if curl -s "http://localhost:8000/health" | grep -q "healthy"; then
        echo "✅ Serviço: Respondendo corretamente"
    else
        echo "❌ Serviço: Não está respondendo ou com problemas"
        return 1
    fi
}

# Function to check authentication
check_auth() {
    echo ""
    echo "2. Verificando autenticação..."
    TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=admin" | jq -r '.data.access_token' 2>/dev/null)
    
    if [ "$TOKEN" != "null" ] && [ "$TOKEN" != "" ] && [ "$TOKEN" != ".data.access_token" ]; then
        echo "✅ Autenticação: Login funcionando corretamente"
    else
        echo "❌ Autenticação: Problema no login (verifique bcrypt/passlib)"
        return 1
    fi
}

# Function to check database connection
check_database() {
    echo ""
    echo "3. Verificando conexão com banco de dados..."
    RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/admin/dashboard" \
        -H "Authorization: Bearer $TOKEN" | jq -r '.totais.usuarios' 2>/dev/null)
    
    if [ "$RESPONSE" -gt 0 ] 2>/dev/null; then
        echo "✅ Banco de dados: Conexão e consultas funcionando"
    else
        echo "❌ Banco de dados: Problema na conexão ou consultas"
        return 1
    fi
}

# Function to check for common errors in logs
check_logs() {
    echo ""
    echo "4. Verificando logs para erros conhecidos..."
    
    # Check for bcrypt errors
    if docker compose logs app --tail=100 | grep -q "error reading bcrypt version"; then
        echo "❌ Logs: Erro bcrypt detectado - atualize requirements.txt"
        return 1
    fi
    
    # Check for generic database errors
    GENERIC_DB_ERRORS=$(docker compose logs app --tail=100 | grep "Database error:" | grep -v "Database error (" | wc -l)
    if [ "$GENERIC_DB_ERRORS" -gt 5 ]; then
        echo "⚠️ Logs: Muitos erros genéricos de banco ($GENERIC_DB_ERRORS) - revisar tratamento de exceções"
    fi
    
    # Check for validation errors
    VALIDATION_ERRORS=$(docker compose logs app --tail=100 | grep "Field required" | wc -l)
    if [ "$VALIDATION_ERRORS" -gt 10 ]; then
        echo "⚠️ Logs: Muitos erros de validação ($VALIDATION_ERRORS) - verificar documentação da API"
    fi
    
    echo "✅ Logs: Verificação de logs concluída"
}

# Function to provide recommendations
provide_recommendations() {
    echo ""
    echo "=== RECOMENDAÇÕES DE PREVENÇÃO ==="
    echo ""
    echo "Para evitar problemas recorrentes:"
    echo ""
    echo "1. DEPENDÊNCIAS:"
    echo "   - Mantenha as versões específicas no requirements.txt"
    echo "   - Teste sempre após atualizações de dependências"
    echo ""
    echo "2. AUTENTICAÇÃO:"
    echo "   - Use form-data (application/x-www-form-urlencoded) para login"
    echo "   - Documente claramente os formatos de requisição"
    echo ""
    echo "3. LOGS:"
    echo "   - Execute este script periodicamente para monitorar"
    echo "   - Configure alertas para erros críticos"
    echo ""
    echo "4. VALIDAÇÃO:"
    echo "   - Implemente validação client-side quando possível"
    echo "   - Forneça exemplos claros na documentação"
    echo ""
    echo "5. MONITORAMENTO:"
    echo "   - Execute: docker compose logs app --follow"
    echo "   - Configure healthchecks periódicos"
}

# Run all checks
FAILED_CHECKS=0

check_service || ((FAILED_CHECKS++))
check_auth || ((FAILED_CHECKS++))
check_database || ((FAILED_CHECKS++))
check_logs || ((FAILED_CHECKS++))

echo ""
echo "=== RESULTADO FINAL ==="
if [ $FAILED_CHECKS -eq 0 ]; then
    echo "✅ Todos os verificações passaram! Sistema saudável."
else
    echo "❌ $FAILED_CHECKS verificação(ões) falharam. Revisar problemas acima."
fi

provide_recommendations

echo ""
echo "Script executado em: $(date)"