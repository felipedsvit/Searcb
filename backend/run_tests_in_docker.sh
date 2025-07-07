#!/bin/bash

# Script to run tests in Docker environment
# Usage: ./run_tests_in_docker.sh [test_file_path]

set -e

echo "Starting Docker services..."
docker compose up -d db redis

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if database is ready
echo "Checking database connection..."
docker compose exec db pg_isready -U searcb -d searcb_db

echo "Building app container..."
docker compose build app

# Run migrations first
echo "Running database migrations..."
docker compose run --rm app alembic upgrade head

# If a specific test file is provided, run only that test
if [ -n "$1" ]; then
  TEST_PATH=$1
  echo "Running specific test: $TEST_PATH"
  docker compose run --rm app pytest $TEST_PATH -v
else
  # Run all tests
  echo "Running all tests..."
  docker compose run --rm app pytest -v
fi

echo "Tests completed. Cleaning up..."

# Uncomment if you want to stop containers after tests
# docker compose down

echo "Done!"
