#!/bin/bash

# CI/CD script for PostgreSQL SQL review
# This script collects SQL files from the current commit and sends them to the reviewer API
#
# Environment variables:
#   API_URL - API endpoint URL (default: http://localhost:8000)
#   THRESHOLD - Minimum score threshold (default: 70)
#   TARGET_BRANCH - Target branch for environment determination (optional)
#                   If not set, uses current branch
#
# Environment mapping:
#   main/master -> production
#   develop/development -> staging
#   release/* -> staging
#   feature/*, bugfix/*, hotfix/* -> development
#   other -> test

API_URL="${API_URL:-http://localhost:8000}"
THRESHOLD="${THRESHOLD:-70}"

determine_environment() {
    local branch="${TARGET_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"

    echo "Target branch: $branch" >&2

    case "$branch" in
        main|master)
            echo "production"
            ;;
        develop|development)
            echo "staging"
            ;;
        release/*)
            echo "staging"
            ;;
        feature/*|bugfix/*|hotfix/*)
            echo "development"
            ;;
        *)
            echo "test"
            ;;
    esac
}

ENVIRONMENT=$(determine_environment)

echo "Starting PostgreSQL SQL review..."
echo "API URL: $API_URL"
echo "Threshold: $THRESHOLD"
echo "Environment: $ENVIRONMENT"

if ! command -v jq &> /dev/null; then
    echo "Warning: jq not found. Installing..."
    if command -v apt-get &> /dev/null; then
        apt-get update && apt-get install -y jq
    elif command -v yum &> /dev/null; then
        yum install -y jq
    elif command -v brew &> /dev/null; then
        brew install jq
    else
        echo "Error: Cannot install jq. Please install jq manually."
        exit 1
    fi
fi

SQL_FILES=$(git diff --name-only HEAD~1 | grep -E '\.(sql)$' || true)

if [ -z "$SQL_FILES" ]; then
    echo "No SQL files found in the commit. Skipping review."
    exit 0
fi

echo "Found SQL files: $SQL_FILES"

QUERIES_JSON="[]"

for file in $SQL_FILES; do
    if [ -f "$file" ]; then
        SQL_CONTENT=$(cat "$file" | jq -R -s '.')
        QUERY_JSON=$(jq -n \
            --arg sql "$SQL_CONTENT" \
            --arg file "$file" \
            '{
                sql: $sql,
                query_plan: "",
                tables: [],
                server_info: {version: "15.0", file: $file}
            }')
        QUERIES_JSON=$(echo "$QUERIES_JSON" | jq --argjson query "$QUERY_JSON" '. += [$query]')
    fi
done

echo "Sending batch review request..."
RESPONSE=$(curl -s -X POST "$API_URL/review/batch" \
    -H "Content-Type: application/json" \
    -d "{\"queries\": $QUERIES_JSON, \"environment\": \"$ENVIRONMENT\"}")

if [ $? -ne 0 ]; then
    echo "Error: Failed to connect to API at $API_URL"
    exit 1
fi

if [ -z "$RESPONSE" ]; then
    echo "Error: Empty response from API"
    exit 1
fi

echo "Review response received"

OVERALL_SCORE=$(echo "$RESPONSE" | jq -r '.overall_score' 2>/dev/null)
if [ $? -ne 0 ] || [ "$OVERALL_SCORE" = "null" ]; then
    echo "Error: Invalid response format from API"
    echo "Response: $RESPONSE"
    exit 1
fi

PASSED=$(echo "$RESPONSE" | jq -r '.passed' 2>/dev/null)
if [ $? -ne 0 ]; then
    PASSED="false"
fi

echo "Overall score: $OVERALL_SCORE"
echo "Passed: $PASSED"

if [ "$PASSED" = "false" ] || [ "$(echo "$OVERALL_SCORE < $THRESHOLD" | bc -l)" -eq 1 ]; then
    echo "❌ SQL review failed! Score: $OVERALL_SCORE (threshold: $THRESHOLD)"
    echo "Issues found:"
    echo "$RESPONSE" | jq -r '.results[] | select(.overall_score < 70) | "  - \(.issues[0].content // "Unknown issue")"'
    exit 1
else
    echo "✅ SQL review passed! Score: $OVERALL_SCORE"
    exit 0
fi
