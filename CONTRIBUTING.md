# Contributing to Kairos

First off, thank you for considering contributing to Kairos! 🎉 It's people like you that make Kairos such a great tool for intelligent scheduling and calendar management.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Style Guidelines](#style-guidelines)
- [Commit Guidelines](#commit-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Community](#community)

## 📜 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** with [uv](https://github.com/astral-sh/uv) package manager
- **Node.js 18+** with npm
- **Git** for version control
- **Docker** (optional, recommended for full-stack development)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/kairos.git
cd kairos
```

3. Add the original repository as upstream:

```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/kairos.git
```

## 🛠️ Development Setup

### Quick Setup with Docker

```bash
# Copy environment variables
cp env.example .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Setup

#### Backend Setup

```bash
cd backend

# Install dependencies
uv sync --dev

# Set up environment variables
cp ../env.example .env

# Run migrations
uv run python migrate.py

# Start development server
uv run python main.py
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp ../env.example .env.local

# Start development server
npm run dev
```

### Verify Installation

- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000

## 🤝 How to Contribute

### Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/your-username/kairos/issues) to avoid duplicates.

When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots and animated GIFs if possible**
- **Include your environment details**:
  - OS version
  - Python version
  - Node.js version
  - Browser version (for frontend issues)

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/your-username/kairos/issues). When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and expected behavior**
- **Explain why this enhancement would be useful**
- **List some other applications where this enhancement exists**

### Pull Requests

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our [style guidelines](#style-guidelines)

3. **Add tests** for your changes (see [Testing](#testing))

4. **Update documentation** if needed

5. **Commit your changes** following our [commit guidelines](#commit-guidelines)

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots/GIFs for UI changes
   - Test results

### Areas for Contribution

We welcome contributions in these areas:

#### 🐛 Bug Fixes
- Fix reported issues
- Improve error handling
- Performance optimizations

#### ✨ Features
- New scheduling algorithms
- UI/UX improvements
- Integration with external calendars
- Mobile app development

#### 📚 Documentation
- API documentation
- User guides
- Code comments
- Translation

#### 🧪 Testing
- Add test coverage
- E2E testing
- Performance testing
- Security testing

## 📝 Style Guidelines

### Python (Backend)

We use several tools to maintain code quality:

```bash
# Format code
uv run black .

# Sort imports
uv run isort .

# Type checking
uv run mypy src/

# Run all checks
uv run pre-commit run --all-files
```

**Code Style:**
- Follow [PEP 8](https://pep8.org/)
- Use type hints for all functions
- Write docstrings for classes and functions
- Keep functions small and focused
- Use meaningful variable names

**Example:**
```python
from typing import List, Optional
from datetime import datetime

def create_event(
    title: str, 
    start_time: datetime, 
    duration_minutes: int,
    category_id: Optional[int] = None
) -> Event:
    """Create a new event with automatic scheduling.
    
    Args:
        title: The event title
        start_time: When the event should start
        duration_minutes: Event duration in minutes
        category_id: Optional category ID
        
    Returns:
        The created event instance
        
    Raises:
        ConflictError: If the time slot is not available
    """
    # Implementation here
    pass
```

### TypeScript/React (Frontend)

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

**Code Style:**
- Use TypeScript for all files
- Use functional components with hooks
- Follow React best practices
- Use meaningful component and prop names
- Write JSDoc comments for complex functions

**Example:**
```typescript
interface EventCardProps {
  event: Event;
  onEdit: (event: Event) => void;
  onDelete: (eventId: string) => void;
}

/**
 * EventCard component displays an event with edit/delete actions
 */
export const EventCard: React.FC<EventCardProps> = ({ 
  event, 
  onEdit, 
  onDelete 
}) => {
  const handleEdit = useCallback(() => {
    onEdit(event);
  }, [event, onEdit]);

  return (
    <Card className="event-card">
      {/* Component implementation */}
    </Card>
  );
};
```

### Database

- Use descriptive table and column names
- Write migrations for schema changes
- Include rollback functionality
- Add indexes for frequently queried columns

## 📝 Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Examples

```bash
feat(scheduler): add conflict detection for overlapping events

fix(auth): resolve GitHub OAuth callback error

docs(api): update event creation endpoint documentation

test(scheduler): add unit tests for priority-based scheduling

chore(deps): update FastAPI to version 0.104.1
```

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_scheduler.py -v

# Run tests with debugging
uv run pytest tests/test_api.py -v -s
```

### Frontend Testing

```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run tests in watch mode
npm run test:watch
```

### Test Guidelines

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Test both success and error cases
- Mock external dependencies

**Example Test:**
```python
def test_create_event_with_conflict():
    """Test event creation when there's a scheduling conflict."""
    # Arrange
    existing_event = create_test_event(
        start_time=datetime(2024, 1, 15, 10, 0),
        duration_minutes=60
    )
    
    # Act & Assert
    with pytest.raises(ConflictError) as exc_info:
        create_event(
            title="Conflicting Event",
            start_time=datetime(2024, 1, 15, 10, 30),
            duration_minutes=60
        )
    
    assert "scheduling conflict" in str(exc_info.value)
```

## 📚 Documentation

### API Documentation

- API endpoints are automatically documented with FastAPI
- Update docstrings for all endpoints
- Include request/response examples

### Code Documentation

- Write clear docstrings for all public functions
- Comment complex algorithms
- Update README files when adding features

### User Documentation

- Update user guides for new features
- Include screenshots for UI changes
- Write troubleshooting guides

## 👥 Community

### Getting Help

- **GitHub Discussions**: For questions and community support
- **GitHub Issues**: For bug reports and feature requests
- **Discord**: [Join our Discord server](https://discord.gg/your-invite) for real-time chat

### Maintainers

Current maintainers:
- [@maintainer1](https://github.com/maintainer1) - Backend & Infrastructure
- [@maintainer2](https://github.com/maintainer2) - Frontend & UI/UX

### Review Process

1. **Automated Checks**: All PRs must pass CI/CD checks
2. **Code Review**: At least one maintainer must approve
3. **Testing**: All tests must pass
4. **Documentation**: Updates must include relevant documentation

### Release Process

We follow [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

## 🏆 Recognition

Contributors are recognized in:
- GitHub contributors page
- Changelog for each release
- Special thanks in release notes

## 📞 Questions?

Don't hesitate to ask questions! You can:

- Open a [GitHub Discussion](https://github.com/your-username/kairos/discussions)
- Create an [Issue](https://github.com/your-username/kairos/issues) with the `question` label
- Reach out to maintainers directly

Thank you for contributing to Kairos! 🚀
