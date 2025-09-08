# API Versioning Guide

## Overview

PostgreSQL Reviewer API supports versioning to ensure backward compatibility and smooth migration to new API versions.

## Current API Structure

### API v1 (Current)

- **Base URL**: `/api/v1/`
- **Status**: Active and stable
- **Documentation**:
  - Swagger UI: `http://localhost:8000/api/v1/docs`
  - ReDoc: `http://localhost:8000/api/v1/redoc`
  - OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`

### Legacy API (Backward Compatibility)

- **Base URL**: `/api/`
- **Status**: Redirects to `/api/v1/`
- **Purpose**: Backward compatibility for existing integrations

## Version Information Endpoint

Get information about supported API versions:

```bash
curl "http://localhost:8000/api/versions"
```

Response:

```json
{
  "current_version": "v1",
  "supported_versions": ["v1"],
  "deprecated_versions": [],
  "endpoints": {
    "v1": {
      "docs": "/api/v1/docs",
      "redoc": "/api/v1/redoc",
      "openapi": "/api/v1/openapi.json"
    }
  }
}
```

## Migration Examples

### Old API Format (still works)

```bash
# Legacy endpoints (redirect to v1)
curl "http://localhost:8000/api/connections/"
curl "http://localhost:8000/api/scheduler/tasks"
curl "http://localhost:8000/api/review/analyze"
```

### New API Format (recommended)

```bash
# Version 1 endpoints (direct)
curl "http://localhost:8000/api/v1/connections/"
curl "http://localhost:8000/api/v1/scheduler/tasks"
curl "http://localhost:8000/api/v1/review/analyze"
```

## Available Endpoints

All endpoints are available under both formats:

### Connections

- `GET /api/v1/connections/` - List all connections
- `POST /api/v1/connections/` - Create new connection
- `GET /api/v1/connections/{id}` - Get connection by ID
- `PUT /api/v1/connections/{id}` - Update connection
- `DELETE /api/v1/connections/{id}` - Delete connection

### Scheduler

- `GET /api/v1/scheduler/tasks` - List all tasks
- `POST /api/v1/scheduler/tasks` - Create new task
- `GET /api/v1/scheduler/tasks/{id}` - Get task by ID
- `PUT /api/v1/scheduler/tasks/{id}` - Update task
- `DELETE /api/v1/scheduler/tasks/{id}` - Delete task
- `POST /api/v1/scheduler/tasks/{id}/run` - Run task immediately

### Review

- `POST /api/v1/review/analyze` - Analyze SQL query
- `POST /api/v1/review/batch` - Batch analyze multiple queries

### Rules

- `GET /api/v1/rules/` - List all rules
- `POST /api/v1/rules/` - Create new rule
- `GET /api/v1/rules/{id}` - Get rule by ID
- `PUT /api/v1/rules/{id}` - Update rule
- `DELETE /api/v1/rules/{id}` - Delete rule

### Monitoring

- `GET /api/v1/monitoring/health` - System health check
- `GET /api/v1/monitoring/stats` - System statistics

## Best Practices

### For New Integrations

- Always use versioned endpoints (`/api/v1/`)
- Check version compatibility using `/api/versions`
- Monitor deprecation notices in API responses

### For Existing Integrations

- Legacy endpoints continue to work
- Plan migration to versioned endpoints
- Test with both formats during transition

### Client Configuration

```python
# Python example
BASE_URL = "http://localhost:8000/api/v1"  # Recommended
# BASE_URL = "http://localhost:8000/api"  # Legacy (still works)

def get_connections():
    return requests.get(f"{BASE_URL}/connections/")
```

```javascript
// JavaScript example
const BASE_URL = "http://localhost:8000/api/v1"; // Recommended
// const BASE_URL = "http://localhost:8000/api";  // Legacy (still works)

const getConnections = () => fetch(`${BASE_URL}/connections/`);
```

## Future Versioning

When new major versions are released:

- Previous versions remain available
- Deprecation schedule will be announced
- Migration guides will be provided
- Breaking changes will be documented

## Testing Both Versions

```bash
# Test v1 endpoint
curl "http://localhost:8000/api/v1/connections/" | jq .

# Test legacy endpoint (redirects to v1)
curl "http://localhost:8000/api/connections/" | jq .

# Verify they return identical results
diff <(curl -s "http://localhost:8000/api/v1/connections/") \
     <(curl -s "http://localhost:8000/api/connections/")
```
