#!/bin/bash

# Script to verify all implemented endpoints are working correctly
# This script will start the Docker services, run the app, and use curl to test each endpoint

set -e

# Configuration
API_BASE="http://localhost:8000/api/v1"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="admin"
REGULAR_USERNAME="user"
REGULAR_PASSWORD="password"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log output
log() {
  echo -e "${GREEN}[$(date +%T)]${NC} $1" >&2
}

# Function to log error
error() {
  echo -e "${RED}[$(date +%T)] ERROR:${NC} $1" >&2
}

# Function to log warning
warn() {
  echo -e "${YELLOW}[$(date +%T)] WARNING:${NC} $1" >&2
}

# Start Docker services
log "Starting Docker services..."
docker compose up -d

# Wait for services to be ready
log "Waiting for services to be ready (30s)..."
sleep 30

# Function to get a JWT token
get_token() {
  local username=$1
  local password=$2
  
  log "Getting token for $username..."
  
  local response=$(curl -s -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$username&password=$password")
  
  # Extract token from response (nested in data.access_token)
  local token=$(echo $response | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')
  
  if [ -z "$token" ]; then
    error "Failed to get token for $username"
    echo $response >&2
    return 1
  else
    log "Successfully got token for $username"
    echo $token
  fi
}

# Function to test an endpoint
test_endpoint() {
  local method=$1
  local endpoint=$2
  local token=$3
  local data=$4
  local expected_status=$5
  local description=$6
  
  log "Testing $description ($method $endpoint)..."
  
  local headers=()
  if [ ! -z "$token" ]; then
    headers+=(-H "Authorization: Bearer $token")
  fi
  
  local status_code
  local response
  
  if [ "$method" == "GET" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE$endpoint" "${headers[@]}")
  elif [ "$method" == "POST" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_BASE$endpoint" \
      -H "Content-Type: application/json" \
      "${headers[@]}" \
      -d "$data")
  elif [ "$method" == "PUT" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$API_BASE$endpoint" \
      -H "Content-Type: application/json" \
      "${headers[@]}" \
      -d "$data")
  fi
  
  if [ "$response" -eq "$expected_status" ]; then
    log "✅ $description succeeded ($response)"
    return 0
  else
    error "❌ $description failed (expected $expected_status, got $response)"
    # Get full response for debugging
    if [ "$method" == "GET" ]; then
      curl -v "$API_BASE$endpoint" "${headers[@]}"
    elif [ "$method" == "POST" ]; then
      curl -v -X POST "$API_BASE$endpoint" \
        -H "Content-Type: application/json" \
        "${headers[@]}" \
        -d "$data"
    elif [ "$method" == "PUT" ]; then
      curl -v -X PUT "$API_BASE$endpoint" \
        -H "Content-Type: application/json" \
        "${headers[@]}" \
        -d "$data"
    fi
    return 1
  fi
}

# Get tokens for both user types
admin_token=$(get_token $ADMIN_USERNAME $ADMIN_PASSWORD)
user_token=$(get_token $REGULAR_USERNAME $REGULAR_PASSWORD)

if [ -z "$admin_token" ] || [ -z "$user_token" ]; then
  error "Could not get authentication tokens. Aborting tests."
  exit 1
fi

# Test health endpoint (note: this is not under /api/v1)
log "Testing Health check (GET /health)..."
health_response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health")
if [ "$health_response" -eq "200" ]; then
  log "✅ Health check succeeded ($health_response)"
else
  error "❌ Health check failed (expected 200, got $health_response)"
  curl -v "http://localhost:8000/health"
  exit 1
fi

# Test Admin Endpoints
log "Testing Admin Endpoints..."
test_endpoint "GET" "/admin/logs" "$admin_token" "" 200 "List logs (admin)"
test_endpoint "GET" "/admin/logs" "$user_token" "" 403 "List logs (regular user - should be forbidden)"
test_endpoint "GET" "/admin/configuracoes" "$admin_token" "" 200 "List configurations (admin)"
test_endpoint "GET" "/admin/configuracoes" "$user_token" "" 403 "List configurations (regular user - should be forbidden)"
test_endpoint "PUT" "/admin/configuracoes/pncp_sync_interval" "$admin_token" '{"valor": "7200"}' 200 "Update configuration (admin)"
test_endpoint "PUT" "/admin/configuracoes/pncp_sync_interval" "$user_token" '{"valor": "7200"}' 403 "Update configuration (regular user - should be forbidden)"

# Test Webhook Endpoints
log "Testing Webhook Endpoints..."
test_endpoint "POST" "/webhooks/interno/notification" "$admin_token" '{
  "tipo": "contrato_vencendo",
  "dados": {
    "contrato_id": 1,
    "numero_contrato": "CT-2024-001",
    "dias_vencimento": 30
  },
  "origem": "sistema_monitoramento",
  "prioridade": "alta"
}' 200 "Webhook notification (admin)"

# Test User Profile Endpoints
log "Testing User Profile Endpoints..."
test_endpoint "GET" "/usuarios/me/profile" "$user_token" "" 200 "Get user profile"
test_endpoint "PUT" "/usuarios/me/profile" "$user_token" '{
  "nome_completo": "User Updated",
  "telefone": "987654321",
  "cargo": "Analista Senior"
}' 200 "Update user profile"

# Test Password Change
log "Testing Password Change..."
test_endpoint "POST" "/usuarios/2/change-password" "$user_token" '{
  "senha_atual": "password",
  "nova_senha": "new_password123"
}' 200 "User changes own password"
test_endpoint "POST" "/usuarios/2/change-password" "$admin_token" '{
  "nova_senha": "admin_set_password"
}' 200 "Admin changes user password"
test_endpoint "POST" "/usuarios/1/change-password" "$user_token" '{
  "nova_senha": "hack_attempt"
}' 403 "User attempts to change admin password (should be forbidden)"

log "All endpoint tests completed!"

# Check for any failures
if [ $? -ne 0 ]; then
  error "Some tests failed. Please review the output."
  exit 1
else
  log "All tests passed successfully!"
fi

# Keep containers running unless explicitly stopped
log "Docker services are still running. Use 'docker compose down' to stop them."
