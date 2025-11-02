# API Documentation

This document provides detailed information about the Kairos REST API endpoints.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com`

## Authentication

All API endpoints require authentication using GitHub OAuth tokens.

```http
Authorization: Bearer <your_jwt_token>
```

### Authentication Flow

1. **Redirect to GitHub OAuth**:
   ```
   GET https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=user:email
   ```

2. **Exchange code for token**:
   ```http
   POST /auth/github/callback
   Content-Type: application/json
   
   {
     "code": "github_oauth_code"
   }
   ```

3. **Response**:
   ```json
   {
     "access_token": "jwt_token_here",
     "token_type": "bearer",
     "user": {
       "id": 1,
       "github_id": 12345,
       "username": "john_doe",
       "email": "john@example.com",
       "avatar_url": "https://github.com/avatar.jpg"
     }
   }
   ```

## Events API

### List Events

```http
GET /events
```

**Query Parameters:**

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `limit` | integer | Number of events to return | 50 |
| `offset` | integer | Number of events to skip | 0 |
| `category_id` | integer | Filter by category ID | - |
| `priority` | string | Filter by priority (high, medium, low) | - |
| `start_date` | string | Filter events after this date (ISO 8601) | - |
| `end_date` | string | Filter events before this date (ISO 8601) | - |
| `is_flexible` | boolean | Filter by flexibility | - |

**Example Request:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/events?limit=10&category_id=1&priority=high"
```

**Response:**
```json
{
  "events": [
    {
      "id": 1,
      "title": "Team Meeting",
      "description": "Weekly team sync",
      "start_time": "2024-01-15T10:00:00Z",
      "end_time": "2024-01-15T11:00:00Z",
      "duration_minutes": 60,
      "location": "Conference Room A",
      "priority": "high",
      "is_flexible": false,
      "category": {
        "id": 1,
        "name": "Work",
        "color_code": "#3B82F6",
        "description": "Work-related events"
      },
      "created_at": "2024-01-10T08:00:00Z",
      "updated_at": "2024-01-10T08:00:00Z"
    }
  ],
  "total": 25,
  "limit": 10,
  "offset": 0
}
```

### Create Event

```http
POST /events
```

**Request Body:**
```json
{
  "title": "Project Review",
  "description": "Review project progress and next steps",
  "start_time": "2024-01-20T14:00:00Z",
  "duration_minutes": 90,
  "location": "Meeting Room B",
  "priority": "high",
  "is_flexible": false,
  "category_id": 1
}
```

**Response:**
```json
{
  "id": 2,
  "title": "Project Review",
  "description": "Review project progress and next steps",
  "start_time": "2024-01-20T14:00:00Z",
  "end_time": "2024-01-20T15:30:00Z",
  "duration_minutes": 90,
  "location": "Meeting Room B",
  "priority": "high",
  "is_flexible": false,
  "category": {
    "id": 1,
    "name": "Work",
    "color_code": "#3B82F6",
    "description": "Work-related events"
  },
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T09:00:00Z"
}
```

### Get Event

```http
GET /events/{id}
```

**Response:**
```json
{
  "id": 1,
  "title": "Team Meeting",
  "description": "Weekly team sync",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T11:00:00Z",
  "duration_minutes": 60,
  "location": "Conference Room A",
  "priority": "high",
  "is_flexible": false,
  "category": {
    "id": 1,
    "name": "Work",
    "color_code": "#3B82F6",
    "description": "Work-related events"
  },
  "created_at": "2024-01-10T08:00:00Z",
  "updated_at": "2024-01-10T08:00:00Z"
}
```

### Update Event

```http
PUT /events/{id}
```

**Request Body:**
```json
{
  "title": "Updated Team Meeting",
  "description": "Updated weekly team sync",
  "start_time": "2024-01-15T11:00:00Z",
  "duration_minutes": 45,
  "priority": "medium"
}
```

### Delete Event

```http
DELETE /events/{id}
```

**Response:**
```json
{
  "message": "Event deleted successfully"
}
```

### Schedule Event Automatically

```http
POST /events/schedule
```

**Request Body:**
```json
{
  "title": "Flexible Meeting",
  "description": "This meeting can be scheduled automatically",
  "preferred_start_time": "2024-01-20T14:00:00Z",
  "duration_minutes": 60,
  "priority": "medium",
  "is_flexible": true,
  "category_id": 1,
  "constraints": {
    "earliest_time": "2024-01-20T09:00:00Z",
    "latest_time": "2024-01-20T17:00:00Z",
    "exclude_days": ["saturday", "sunday"]
  }
}
```

**Response:**
```json
{
  "id": 3,
  "title": "Flexible Meeting",
  "scheduled_time": "2024-01-20T15:00:00Z",
  "end_time": "2024-01-20T16:00:00Z",
  "conflicts_resolved": [
    {
      "original_event_id": 2,
      "action": "moved",
      "new_time": "2024-01-20T16:30:00Z"
    }
  ],
  "scheduling_score": 0.85
}
```

## Categories API

### List Categories

```http
GET /categories
```

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Work",
      "color_code": "#3B82F6",
      "description": "Work-related events",
      "event_count": 15,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "Personal",
      "color_code": "#10B981",
      "description": "Personal activities",
      "event_count": 8,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Create Category

```http
POST /categories
```

**Request Body:**
```json
{
  "name": "Health",
  "color_code": "#EF4444",
  "description": "Health and medical appointments"
}
```

### Update Category

```http
PUT /categories/{id}
```

**Request Body:**
```json
{
  "name": "Healthcare",
  "color_code": "#DC2626",
  "description": "Health, medical, and wellness appointments"
}
```

### Delete Category

```http
DELETE /categories/{id}
```

## Schedule API

### Get Daily Schedule

```http
GET /schedule/daily
```

**Query Parameters:**

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `date` | string | Date in ISO 8601 format | Yes |
| `timezone` | string | Timezone (e.g., "America/New_York") | No |

**Example:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/schedule/daily?date=2024-01-15T00:00:00Z"
```

**Response:**
```json
{
  "date": "2024-01-15",
  "timezone": "UTC",
  "events": [
    {
      "id": 1,
      "title": "Morning Standup",
      "start_time": "2024-01-15T09:00:00Z",
      "end_time": "2024-01-15T09:30:00Z",
      "category": {
        "name": "Work",
        "color_code": "#3B82F6"
      }
    }
  ],
  "free_slots": [
    {
      "start_time": "2024-01-15T09:30:00Z",
      "end_time": "2024-01-15T10:00:00Z",
      "duration_minutes": 30
    }
  ],
  "total_scheduled_minutes": 480,
  "total_free_minutes": 480
}
```

### Get Weekly Schedule

```http
GET /schedule/weekly
```

**Query Parameters:**

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `start_date` | string | Week start date in ISO 8601 format | Yes |
| `timezone` | string | Timezone | No |

**Response:**
```json
{
  "week_start": "2024-01-15",
  "week_end": "2024-01-21",
  "timezone": "UTC",
  "days": [
    {
      "date": "2024-01-15",
      "events": [...],
      "total_scheduled_minutes": 480
    }
  ],
  "week_summary": {
    "total_events": 25,
    "total_scheduled_minutes": 2400,
    "average_daily_minutes": 480,
    "busiest_day": "2024-01-17",
    "categories_breakdown": {
      "Work": 60,
      "Personal": 25,
      "Health": 15
    }
  }
}
```

## Conflicts API

### Detect Conflicts

```http
POST /conflicts/detect
```

**Request Body:**
```json
{
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T11:00:00Z"
}
```

**Response:**
```json
{
  "has_conflicts": true,
  "conflicts": [
    {
      "event_id": 1,
      "event_title": "Existing Meeting",
      "overlap_start": "2024-01-15T10:00:00Z",
      "overlap_end": "2024-01-15T10:30:00Z",
      "overlap_minutes": 30
    }
  ]
}
```

### Resolve Conflicts

```http
POST /conflicts/resolve
```

**Request Body:**
```json
{
  "new_event": {
    "title": "Important Meeting",
    "start_time": "2024-01-15T10:00:00Z",
    "duration_minutes": 60,
    "priority": "high"
  },
  "resolution_strategy": "reschedule_flexible",
  "constraints": {
    "max_reschedule_hours": 24,
    "preserve_high_priority": true
  }
}
```

**Response:**
```json
{
  "resolution": {
    "new_event_scheduled": true,
    "new_event_time": "2024-01-15T10:00:00Z",
    "conflicts_resolved": [
      {
        "event_id": 2,
        "original_time": "2024-01-15T10:30:00Z",
        "new_time": "2024-01-15T14:00:00Z",
        "action": "rescheduled"
      }
    ]
  },
  "alternative_solutions": [
    {
      "description": "Schedule at 2 PM instead",
      "new_event_time": "2024-01-15T14:00:00Z",
      "conflicts_resolved": []
    }
  ]
}
```

## AI Assistant API

### AI-Powered Scheduling

```http
POST /assistant/schedule
```

**Request Body:**
```json
{
  "query": "Schedule a 2-hour deep work session this week, preferably in the morning",
  "constraints": {
    "duration_minutes": 120,
    "preferred_times": ["morning"],
    "exclude_days": ["friday"],
    "category_id": 1
  }
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "title": "Deep Work Session",
      "start_time": "2024-01-16T09:00:00Z",
      "end_time": "2024-01-16T11:00:00Z",
      "confidence_score": 0.92,
      "reasoning": "Optimal morning slot with no conflicts and high focus potential"
    }
  ],
  "ai_analysis": {
    "productivity_insights": "Morning slots show 85% higher completion rates for deep work",
    "conflict_analysis": "No conflicts detected for suggested times",
    "optimization_suggestions": [
      "Consider blocking calendar 15 minutes before for preparation"
    ]
  }
}
```

### Analyze Schedule Patterns

```http
POST /assistant/analyze
```

**Request Body:**
```json
{
  "analysis_type": "productivity",
  "time_range": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z"
  }
}
```

**Response:**
```json
{
  "analysis": {
    "productivity_patterns": {
      "peak_hours": ["09:00-11:00", "14:00-16:00"],
      "low_energy_periods": ["13:00-14:00"],
      "most_productive_days": ["tuesday", "wednesday"]
    },
    "scheduling_insights": [
      "You complete 90% more tasks when scheduled between 9-11 AM",
      "Friday afternoons show 60% higher cancellation rates"
    ],
    "recommendations": [
      "Schedule important meetings on Tuesday/Wednesday mornings",
      "Block Friday afternoons for flexible or low-priority tasks"
    ]
  }
}
```

## Goals API

### List Goals

```http
GET /goals
```

**Response:**
```json
{
  "goals": [
    {
      "id": 1,
      "title": "Exercise 3 times per week",
      "description": "Maintain regular exercise routine",
      "target_value": 3,
      "current_value": 2,
      "unit": "times_per_week",
      "category_id": 3,
      "status": "in_progress",
      "created_at": "2024-01-01T00:00:00Z",
      "deadline": "2024-12-31T23:59:59Z"
    }
  ]
}
```

### Create Goal

```http
POST /goals
```

**Request Body:**
```json
{
  "title": "Read 2 books per month",
  "description": "Improve knowledge through regular reading",
  "target_value": 2,
  "unit": "books_per_month",
  "category_id": 2,
  "deadline": "2024-12-31T23:59:59Z"
}
```

## Health Check

### Service Health

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:00:00Z",
  "version": "0.1.0",
  "services": {
    "database": "healthy",
    "api": "healthy",
    "ai_service": "healthy"
  },
  "uptime_seconds": 86400
}
```

## Error Responses

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource conflict (e.g., scheduling) |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Event title is required",
    "details": {
      "field": "title",
      "validation": "required"
    },
    "timestamp": "2024-01-15T10:00:00Z",
    "request_id": "req_123456789"
  }
}
```

## Rate Limiting

API requests are rate limited:

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated**: 100 requests per hour

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## Webhooks

### Event Notifications

Subscribe to event notifications:

```http
POST /webhooks
```

**Request Body:**
```json
{
  "url": "https://your-app.com/webhooks/kairos",
  "events": ["event.created", "event.updated", "conflict.detected"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload

```json
{
  "event": "event.created",
  "data": {
    "event": {
      "id": 1,
      "title": "New Meeting",
      "start_time": "2024-01-15T10:00:00Z"
    }
  },
  "timestamp": "2024-01-15T09:45:00Z",
  "webhook_id": "wh_123456789"
}
```

## SDKs and Libraries

### JavaScript/TypeScript

```bash
npm install @kairos/api-client
```

```typescript
import { KairosClient } from '@kairos/api-client';

const client = new KairosClient({
  apiUrl: 'https://api.kairos-app.com',
  token: 'your_jwt_token'
});

const events = await client.events.list({
  limit: 10,
  category_id: 1
});
```

### Python

```bash
pip install kairos-api-client
```

```python
from kairos import KairosClient

client = KairosClient(
    api_url='https://api.kairos-app.com',
    token='your_jwt_token'
)

events = client.events.list(limit=10, category_id=1)
```

---

For more information, visit the [interactive API documentation](http://localhost:8000/docs) when running the development server.
