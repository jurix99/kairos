# Development Guide

This guide covers the development workflow, architecture decisions, and best practices for contributing to Kairos.

## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│   (Next.js)     │    │   (FastAPI)     │    │   (SQLite/      │
│                 │    │                 │    │    PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   GitHub OAuth  │    │   OpenAI API    │    │   Migrations    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Backend Architecture

```
backend/src/kairos_backend/
├── config/          # Configuration management
│   ├── auth.py      # Authentication configuration
│   ├── database.py  # Database configuration
│   └── settings.py  # Application settings
├── models/          # Data models
│   ├── database.py  # SQLAlchemy models
│   └── schemas.py   # Pydantic schemas
├── routes/          # API endpoints
│   ├── auth.py      # Authentication routes
│   ├── events.py    # Event management
│   ├── categories.py # Category management
│   ├── scheduling.py # Scheduling logic
│   └── assistant.py # AI assistant
└── services/        # Business logic
    ├── auth_service.py
    ├── event_service.py
    ├── scheduler_service.py
    └── assistant_service.py
```

### Frontend Architecture

```
frontend/
├── app/             # Next.js App Router
│   ├── layout.tsx   # Root layout
│   ├── page.tsx     # Home page
│   ├── login/       # Authentication
│   ├── dashboard/   # Main dashboard
│   ├── calendar/    # Calendar views
│   └── settings/    # User settings
├── components/      # React components
│   ├── ui/          # Base UI components
│   ├── forms/       # Form components
│   └── charts/      # Chart components
├── contexts/        # React contexts
│   ├── auth-context.tsx
│   └── settings-context.tsx
└── lib/             # Utilities
    ├── api.ts       # API client
    ├── utils.ts     # Utility functions
    └── colors.ts    # Color utilities
```

## 🛠️ Development Workflow

### 1. Setting Up Development Environment

#### Prerequisites
- Python 3.11+ with [uv](https://github.com/astral-sh/uv)
- Node.js 18+ with npm
- Git
- Docker (optional but recommended)

#### Quick Setup
```bash
# Clone the repository
git clone https://github.com/your-username/kairos.git
cd kairos

# Set up environment
cp env.example .env

# Start with Docker (recommended)
docker-compose up -d

# Or manual setup
make dev-setup
make dev-start
```

### 2. Development Commands

#### Backend Development
```bash
cd backend

# Install dependencies
uv sync --dev

# Run migrations
uv run python migrate.py

# Start development server
uv run python main.py

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy src/
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build

# Lint and format
npm run lint
npm run format
```

### 3. Database Development

#### Creating Migrations
```bash
cd backend

# Create a new migration
uv run alembic revision --autogenerate -m "Add new feature"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

#### Database Schema
```sql
-- Core tables
Events (id, title, description, start_time, end_time, ...)
Categories (id, name, color_code, description)
Users (id, github_id, username, email, ...)

-- Relationships
Event.category_id -> Category.id
Event.user_id -> User.id
```

## 🧪 Testing Strategy

### Backend Testing

#### Test Structure
```
tests/
├── __init__.py
├── conftest.py         # Pytest configuration
├── test_api.py         # API endpoint tests
├── test_models.py      # Model tests
├── test_services.py    # Service layer tests
└── test_scheduler.py   # Scheduling logic tests
```

#### Writing Tests
```python
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_create_event_success(client: TestClient, auth_headers):
    """Test successful event creation."""
    event_data = {
        "title": "Test Event",
        "start_time": "2024-01-15T10:00:00",
        "duration_minutes": 60,
        "category_id": 1
    }
    
    response = client.post(
        "/events", 
        json=event_data, 
        headers=auth_headers
    )
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Event"
```

#### Test Categories
- **Unit Tests**: Individual functions and methods
- **Integration Tests**: API endpoints with database
- **Service Tests**: Business logic validation
- **Scheduling Tests**: Conflict detection and resolution

### Frontend Testing

#### Test Structure
```
frontend/
├── __tests__/          # Test files
├── components/__tests__/ # Component tests
├── lib/__tests__/      # Utility tests
└── e2e/               # E2E tests
```

#### Writing Component Tests
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { EventCard } from '../EventCard';

test('renders event card with correct data', () => {
  const mockEvent = {
    id: '1',
    title: 'Test Event',
    start_time: '2024-01-15T10:00:00',
    category: { name: 'Work', color_code: '#3B82F6' }
  };

  render(<EventCard event={mockEvent} />);
  
  expect(screen.getByText('Test Event')).toBeInTheDocument();
  expect(screen.getByText('Work')).toBeInTheDocument();
});
```

## 🔄 API Development

### API Design Principles
- **RESTful**: Follow REST conventions
- **Consistent**: Use consistent naming and structure
- **Documented**: Automatic documentation with FastAPI
- **Versioned**: Prepare for future API versions
- **Secure**: Authentication and validation

### Endpoint Structure
```
GET    /api/v1/events          # List events
POST   /api/v1/events          # Create event
GET    /api/v1/events/{id}     # Get event
PUT    /api/v1/events/{id}     # Update event
DELETE /api/v1/events/{id}     # Delete event

GET    /api/v1/categories      # List categories
POST   /api/v1/categories      # Create category

GET    /api/v1/schedule/daily  # Daily schedule
GET    /api/v1/schedule/weekly # Weekly schedule

POST   /api/v1/assistant/schedule # AI scheduling
```

### Request/Response Patterns
```python
# Request Schema
class EventCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_time: datetime
    duration_minutes: int = Field(..., gt=0, le=1440)
    category_id: int
    priority: Priority = Priority.MEDIUM
    is_flexible: bool = False

# Response Schema
class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    category: CategoryResponse
    priority: Priority
    is_flexible: bool
    created_at: datetime
    updated_at: datetime
```

## 🎨 UI/UX Development

### Design System
- **Base**: Tailwind CSS with shadcn/ui components
- **Theme**: Dark theme by default with purple/pink accents
- **Components**: Reusable, accessible components
- **Responsive**: Mobile-first design

### Component Structure
```typescript
interface ComponentProps {
  // Define clear prop interfaces
  title: string;
  optional?: boolean;
  onAction?: (data: ActionData) => void;
}

export const Component: React.FC<ComponentProps> = ({ 
  title, 
  optional = false, 
  onAction 
}) => {
  // Use hooks for state management
  const [state, setState] = useState<StateType>(initialState);
  
  // Memoize expensive calculations
  const expensiveValue = useMemo(() => {
    return calculateExpensiveValue(state);
  }, [state]);
  
  // Handle side effects
  useEffect(() => {
    // Side effect logic
  }, [dependencies]);
  
  return (
    <div className="component-wrapper">
      {/* Component JSX */}
    </div>
  );
};
```

### Styling Guidelines
```css
/* Use Tailwind utility classes */
.card {
  @apply bg-card text-card-foreground rounded-lg border p-6;
}

/* Create component variants */
.card-elevated {
  @apply shadow-lg;
}

/* Use CSS custom properties for dynamic values */
.category-badge {
  background-color: var(--category-color);
}
```

## 🔐 Security Development

### Authentication Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant GitHub

    User->>Frontend: Click "Login with GitHub"
    Frontend->>GitHub: Redirect to OAuth
    GitHub->>Frontend: Return with code
    Frontend->>Backend: Send code
    Backend->>GitHub: Exchange code for token
    GitHub->>Backend: Return user data
    Backend->>Frontend: Return JWT token
    Frontend->>Frontend: Store token
```

### Security Checklist
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (use ORM)
- [ ] XSS protection in frontend
- [ ] CSRF protection for state-changing operations
- [ ] Secure session management
- [ ] Environment variable protection
- [ ] Dependency vulnerability scanning
- [ ] Security headers in production

### Input Validation
```python
from pydantic import BaseModel, Field, validator

class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    start_time: datetime
    duration_minutes: int = Field(..., gt=0, le=1440)
    
    @validator('start_time')
    def validate_start_time(cls, v):
        if v < datetime.now():
            raise ValueError('Start time cannot be in the past')
        return v
```

## 📊 Performance Optimization

### Backend Performance
- **Database**: Use indexes, optimize queries, connection pooling
- **Caching**: Redis for frequently accessed data
- **Async**: Use async/await for I/O operations
- **Pagination**: Limit large result sets

### Frontend Performance
- **Code Splitting**: Lazy load routes and components
- **Caching**: Use React Query for API caching
- **Optimization**: Memoization and virtual scrolling
- **Bundle Size**: Analyze and optimize bundle

### Database Optimization
```python
# Use select_related for relationships
events = session.query(Event)\
    .options(selectinload(Event.category))\
    .filter(Event.user_id == user_id)\
    .limit(50)

# Create indexes for frequent queries
Index('idx_events_user_start', Event.user_id, Event.start_time)
Index('idx_events_category', Event.category_id)
```

## 🚀 Deployment

### Development Deployment
```bash
# Using Docker
docker-compose up -d

# Manual deployment
make deploy-dev
```

### Production Deployment
```bash
# Using Docker
docker-compose -f docker-compose.prod.yml up -d

# Using cloud providers
make deploy-prod
```

### Environment Configuration
```env
# Development
NODE_ENV=development
DATABASE_URL=sqlite:///./kairos.db
DEBUG=true

# Production
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@host:port/db
DEBUG=false
CORS_ORIGINS=https://yourdomain.com
```

## 🔧 Debugging

### Backend Debugging
```python
import logging
import pdb

# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Debug specific issues
def debug_scheduler(events):
    logger.debug(f"Processing {len(events)} events")
    pdb.set_trace()  # Interactive debugging
    # Logic here
```

### Frontend Debugging
```typescript
// React Developer Tools
// Console debugging
console.debug('Component state:', state);

// Performance profiling
import { Profiler } from 'react';

const onRenderCallback = (id, phase, actualDuration) => {
  console.log('Render performance:', { id, phase, actualDuration });
};

<Profiler id="EventList" onRender={onRenderCallback}>
  <EventList />
</Profiler>
```

## 📚 Documentation

### Code Documentation
- **Functions**: Document parameters, return values, exceptions
- **Classes**: Document purpose, usage examples
- **APIs**: Automatic documentation with FastAPI
- **Components**: Document props and usage

### README Updates
- Keep setup instructions current
- Update feature lists
- Maintain troubleshooting guides
- Include architecture diagrams

## 🤝 Collaboration

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Code Review Process
1. **Self Review**: Review your own code first
2. **Automated Checks**: Ensure all CI checks pass
3. **Peer Review**: At least one maintainer approval
4. **Testing**: Verify functionality works as expected
5. **Documentation**: Update relevant documentation

### Communication
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code changes and reviews
- **Discord**: Real-time collaboration (if available)

---

This development guide is a living document. Please update it as the project evolves and new patterns emerge.

