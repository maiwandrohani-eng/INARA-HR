#!/bin/bash

# Test Runner Script for INARA HRIS
# Runs all tests and generates a comprehensive report

echo "🧪 INARA HRIS - Comprehensive Test Suite"
echo "========================================"
echo ""

# Set test environment
export ENVIRONMENT=test
export DATABASE_URL=sqlite+aiosqlite:///:memory:
export DATABASE_ASYNC_URL=sqlite+aiosqlite:///:memory:
export REDIS_URL=redis://localhost:6379
export SECRET_KEY=test-secret-key-for-testing-only
export RATE_LIMIT_ENABLED=false  # Disable rate limiting for tests

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Run tests with coverage
echo "Running tests with pytest..."
echo ""

pytest tests/ \
    -v \
    --tb=short \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=json \
    -p no:warnings \
    "$@"

TEST_EXIT_CODE=$?

echo ""
echo "========================================"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
fi
echo ""

# Show coverage report
if [ -f "htmlcov/index.html" ]; then
    echo "📊 Coverage report generated: htmlcov/index.html"
fi

if [ -f "coverage.json" ]; then
    echo "📊 Coverage JSON generated: coverage.json"
fi

echo ""
echo "Test Results Summary:"
pytest tests/ --collect-only -q 2>/dev/null | tail -1

exit $TEST_EXIT_CODE

