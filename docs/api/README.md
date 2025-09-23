# P3IF API Reference

This document provides comprehensive documentation for the P3IF (Properties, Processes, and Perspectives Inter-Framework) API, including current implementation status and available endpoints.

## 🚀 Current Implementation Status

### ✅ Implemented Features
- **Core Data Models**: BasePattern, Property, Process, Perspective, Relationship with Pydantic V2
- **Framework Operations**: Pattern management, relationship analysis, cross-domain integration
- **Visualization Generation**: PNG, GIF, and interactive HTML output
- **Performance Optimization**: Caching, concurrency, and memory management
- **Output Organization**: Session-based file organization with metadata

### 🚧 In Development
- **RESTful API Endpoints**: Currently implemented as Python modules, REST API in development
- **Authentication System**: Token-based authentication framework
- **Real-time Updates**: WebSocket support for live visualization updates
- **Advanced Analytics**: Machine learning-based pattern recognition

## Overview

The P3IF API provides RESTful endpoints for interacting with P3IF data, generating visualizations, and performing analysis. The API is designed to be language-agnostic and supports JSON for data exchange.

## Base URL

```
http://localhost:5000/api/v1
```

## Authentication

Currently, the API uses simple token-based authentication for development environments. Production deployments should implement OAuth 2.0 or similar enterprise authentication.

### Headers

All API requests should include:

```http
Content-Type: application/json
Authorization: Bearer <your-api-token>
```

## Core Endpoints

### Domains

#### List All Domains

```http
GET /domains
```

**Response:**
```json
{
  "domains": [
    {
      "id": "cybersecurity",
      "name": "Cybersecurity",
      "description": "Security framework for information systems",
      "version": "1.0",
      "properties_count": 15,
      "processes_count": 12,
      "perspectives_count": 8,
      "relationships_count": 234
    }
  ],
  "total": 1
}
```

#### Get Domain Details

```http
GET /domains/{domain_id}
```

**Parameters:**
- `domain_id` (string): Unique identifier for the domain

**Response:**
```json
{
  "id": "cybersecurity",
  "name": "Cybersecurity",
  "description": "Security framework for information systems",
  "version": "1.0",
  "properties": [...],
  "processes": [...],
  "perspectives": [...],
  "relationships": [...],
  "metadata": {
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "source": "NIST Cybersecurity Framework"
  }
}
```

#### Create New Domain

```http
POST /domains
```

**Request Body:**
```json
{
  "name": "Healthcare Security",
  "description": "Healthcare-specific security framework",
  "properties": [...],
  "processes": [...],
  "perspectives": [...]
}
```

### Properties

#### List Properties

```http
GET /domains/{domain_id}/properties
```

**Query Parameters:**
- `page` (integer): Page number for pagination (default: 1)
- `limit` (integer): Number of items per page (default: 20)
- `search` (string): Search term for filtering properties

**Response:**
```json
{
  "properties": [
    {
      "id": "confidentiality",
      "name": "Confidentiality",
      "description": "Ensuring information is accessible only to authorized individuals",
      "domain_id": "cybersecurity",
      "attributes": {
        "category": "security",
        "priority": "high"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 15,
    "pages": 1
  }
}
```

#### Get Property Details

```http
GET /properties/{property_id}
```

#### Create Property

```http
POST /domains/{domain_id}/properties
```

#### Update Property

```http
PUT /properties/{property_id}
```

#### Delete Property

```http
DELETE /properties/{property_id}
```

### Processes

#### List Processes

```http
GET /domains/{domain_id}/processes
```

#### Get Process Details

```http
GET /processes/{process_id}
```

#### Create Process

```http
POST /domains/{domain_id}/processes
```

### Perspectives

#### List Perspectives

```http
GET /domains/{domain_id}/perspectives
```

#### Get Perspective Details

```http
GET /perspectives/{perspective_id}
```

#### Create Perspective

```http
POST /domains/{domain_id}/perspectives
```

### Relationships

#### List Relationships

```http
GET /domains/{domain_id}/relationships
```

**Query Parameters:**
- `property_id` (string): Filter by specific property
- `process_id` (string): Filter by specific process
- `perspective_id` (string): Filter by specific perspective
- `min_strength` (float): Minimum relationship strength (0.0-1.0)
- `min_confidence` (float): Minimum confidence level (0.0-1.0)

**Response:**
```json
{
  "relationships": [
    {
      "id": "rel_001",
      "property_id": "confidentiality",
      "process_id": "encryption",
      "perspective_id": "technical",
      "strength": 0.9,
      "confidence": 0.85,
      "metadata": {
        "source": "expert_assessment",
        "created_at": "2024-01-01T00:00:00Z"
      }
    }
  ]
}
```

#### Create Relationship

```http
POST /domains/{domain_id}/relationships
```

**Request Body:**
```json
{
  "property_id": "confidentiality",
  "process_id": "encryption",
  "perspective_id": "technical",
  "strength": 0.9,
  "confidence": 0.85
}
```

### Cross-Domain Analysis

#### Get Cross-Domain Relationships

```http
GET /cross-domain/relationships
```

**Query Parameters:**
- `domains` (array): List of domain IDs to analyze
- `min_strength` (float): Minimum relationship strength

#### Generate Cross-Domain Mapping

```http
POST /cross-domain/mapping
```

**Request Body:**
```json
{
  "source_domain": "cybersecurity",
  "target_domain": "healthcare",
  "mapping_rules": [
    {
      "source_property": "confidentiality",
      "target_property": "patient_privacy",
      "weight": 0.8
    }
  ]
}
```

## Visualization Endpoints

### Generate Visualization

```http
POST /visualizations/generate
```

**Request Body:**
```json
{
  "type": "3d_cube",
  "domain_id": "cybersecurity",
  "options": {
    "width": 800,
    "height": 600,
    "show_labels": true,
    "color_scheme": "default"
  }
}
```

**Response:**
```json
{
  "visualization_id": "viz_001",
  "type": "3d_cube",
  "status": "ready",
  "url": "/visualizations/viz_001/render",
  "download_url": "/visualizations/viz_001/download"
}
```

### Get Visualization

```http
GET /visualizations/{visualization_id}
```

### List Available Visualization Types

```http
GET /visualizations/types
```

**Response:**
```json
{
  "types": [
    {
      "id": "3d_cube",
      "name": "3D Cube Visualization",
      "description": "Interactive 3D cube showing P3IF relationships",
      "supported_formats": ["html", "png", "svg"]
    },
    {
      "id": "network_graph",
      "name": "Network Graph",
      "description": "Node-link diagram of relationships",
      "supported_formats": ["html", "png", "svg", "json"]
    }
  ]
}
```

## Analysis Endpoints

### Generate Analysis Report

```http
POST /analysis/generate
```

**Request Body:**
```json
{
  "type": "relationship_analysis",
  "domain_id": "cybersecurity",
  "parameters": {
    "include_cross_domain": true,
    "min_strength_threshold": 0.5
  }
}
```

### Get Analysis Results

```http
GET /analysis/{analysis_id}
```

### List Analysis Types

```http
GET /analysis/types
```

## Data Export/Import

### Export Domain Data

```http
GET /domains/{domain_id}/export
```

**Query Parameters:**
- `format` (string): Export format (`json`, `csv`, `excel`)
- `include_relationships` (boolean): Include relationship data

### Import Domain Data

```http
POST /domains/import
```

**Request Body:** Multipart form data with file upload

## Error Handling

The API uses standard HTTP status codes and returns structured error responses:

```json
{
  "error": {
    "code": "DOMAIN_NOT_FOUND",
    "message": "The specified domain was not found",
    "details": {
      "domain_id": "invalid_domain"
    }
  }
}
```

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error

## SDK and Client Libraries

### Python SDK

```python
from p3if import P3IFClient

client = P3IFClient(base_url="http://localhost:5000/api/v1", 
                   token="your-api-token")

# Get all domains
domains = client.domains.list()

# Create a new property
property_data = {
    "name": "Data Integrity",
    "description": "Ensuring data accuracy and consistency"
}
new_property = client.properties.create("cybersecurity", property_data)

# Generate visualization
viz_config = {
    "type": "3d_cube",
    "domain_id": "cybersecurity",
    "options": {"show_labels": True}
}
visualization = client.visualizations.generate(viz_config)
```

### JavaScript SDK

```javascript
import { P3IFClient } from '@p3if/client';

const client = new P3IFClient({
  baseURL: 'http://localhost:5000/api/v1',
  token: 'your-api-token'
});

// Get domain details
const domain = await client.domains.get('cybersecurity');

// Create relationship
const relationship = await client.relationships.create('cybersecurity', {
  property_id: 'confidentiality',
  process_id: 'encryption',
  perspective_id: 'technical',
  strength: 0.9,
  confidence: 0.85
});
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Development**: 1000 requests per hour per IP
- **Production**: 10000 requests per hour per authenticated user

Rate limit information is included in response headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Webhook Support

The API supports webhooks for real-time notifications:

### Webhook Events

- `domain.created`
- `domain.updated`
- `relationship.created`
- `analysis.completed`

### Webhook Configuration

```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/p3if",
  "events": ["domain.created", "relationship.created"],
  "secret": "your-webhook-secret"
}
```

## Versioning

The API uses semantic versioning. Current version is v1. Breaking changes will result in a new version number.

## Support

For API support and questions:
- Documentation: [https://p3if.com/docs/api](https://p3if.com/docs/api)
- Issues: [https://github.com/p3if/p3if/issues](https://github.com/p3if/p3if/issues)
- Email: api-support@p3if.com 