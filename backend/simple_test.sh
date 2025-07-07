#!/bin/bash

# Simple endpoint test script
set -e

API_BASE="http://localhost:8000/api/v1"

echo "Testing health endpoint..."
curl -s "http://localhost:8000/health" | head -c 100
echo ""

echo "Testing login endpoint..."
response=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin")

echo "Login response (first 200 chars):"
echo $response | head -c 200
echo ""

echo "Extracting token..."
token=$(echo $response | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')
echo "Token (first 50 chars): ${token:0:50}..."

echo "Testing admin logs endpoint..."
curl -s -w "\nStatus: %{http_code}\n" \
  -H "Authorization: Bearer $token" \
  "$API_BASE/admin/logs"

echo "Done."
