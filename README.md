# 🚀 Kairos - Intelligent Calendar & Scheduling System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)

> An intelligent calendar and scheduling system with automated conflict resolution, smart scheduling, and AI-powered assistance.

## ✨ Features

### 🎯 Core Functionality
- **Smart Scheduling**: Automatic event placement with conflict detection
- **Priority Management**: High, medium, and low priority system
- **Flexible Events**: Events that can be automatically rescheduled
- **Category System**: Customizable categories with color coding
- **Conflict Resolution**: Intelligent handling of scheduling conflicts

### 🤖 AI-Powered
- **Scheduling Assistant**: AI recommendations for optimal time slots
- **Conflict Analysis**: Smart suggestions for resolving scheduling conflicts
- **Natural Language**: Create events using natural language descriptions

### 🔐 Authentication & Security
- **GitHub OAuth**: Secure authentication with GitHub
- **Session Management**: Persistent user sessions
- **Protected Routes**: Secure access to user data

### 📱 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Modern dark interface with customizable colors
- **Interactive Charts**: Real-time statistics and analytics
- **Calendar Views**: Daily, weekly, and monthly calendar views

## 🏗️ Architecture

```
kairos/
├── backend/          # Python FastAPI backend
│   ├── src/
│   │   └── kairos_backend/
│   │       ├── config/      # Configuration & settings
│   │       ├── models/      # Database models & schemas
│   │       ├── routes/      # API endpoints
│   │       └── services/    # Business logic
│   └── tests/       # Backend tests
├── frontend/        # Next.js React frontend
│   ├── app/         # Next.js app router
│   ├── components/  # React components
│   ├── contexts/    # Context providers
│   └── lib/         # Utilities & API client
└── docs/           # Documentation
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with [uv](https://github.com/astral-sh/uv) package manager
- **Node.js 18+** with npm
- **Git** for version control
- **Docker** (optional, for containerized deployment)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/kairos.git
cd kairos
```

### 2. Set Up Environment Variables

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=sqlite:///./kairos.db

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# OpenAI (for AI assistant)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Start with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs

### 4. Manual Setup (Development)

#### Backend Setup

```bash
cd backend

# Install dependencies
uv sync --dev

# Run database migrations
uv run python migrate.py

# Start the server
uv run python main.py
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create local environment file
cp ../env.example .env.local

# Start development server
npm run dev
```

## 📚 Documentation

### API Documentation
- **Interactive Docs**: http://localhost:8080/docs (Swagger UI)
- **ReDoc**: http://localhost:8080/redoc
- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)

### Setup Guides
- **Frontend Setup**: [frontend/SETUP.md](frontend/SETUP.md)
- **Quick Start**: [frontend/QUICK_START.md](frontend/QUICK_START.md)
- **Docker Guide**: [frontend/DOCKER.md](frontend/DOCKER.md)

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_api.py -v
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

## 🛠️ Development

### Code Quality

We use several tools to maintain code quality:

```bash
# Backend (Python)
cd backend
uv run black .          # Code formatting
uv run isort .          # Import sorting
uv run mypy src/        # Type checking

# Frontend (TypeScript/React)
cd frontend
npm run lint            # ESLint
npm run format          # Prettier
npm run type-check      # TypeScript
```

### Database Management

```bash
cd backend

# Create new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## 🚢 Deployment

### Docker Production

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Manual Deployment

Detailed deployment guides are available in:
- [Backend Deployment](backend/README.md#deployment)
- [Frontend Deployment](frontend/README.md#deployment)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📋 API Endpoints

### Events
| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/events` | List all events with filters |
| POST | `/events` | Create a new event |
| GET | `/events/{id}` | Get event by ID |
| PUT | `/events/{id}` | Update event |
| DELETE | `/events/{id}` | Delete event |
| POST | `/events/schedule` | Auto-schedule flexible event |

### Categories
| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/categories` | List all categories |
| POST | `/categories` | Create category |
| PUT | `/categories/{id}` | Update category |
| DELETE | `/categories/{id}` | Delete category |

### Scheduling
| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/schedule/daily` | Get daily schedule |
| GET | `/schedule/weekly` | Get weekly schedule |
| POST | `/conflicts/resolve` | Resolve scheduling conflict |

### AI Assistant
| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/assistant/schedule` | AI-powered scheduling |
| POST | `/assistant/analyze` | Analyze scheduling patterns |

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./kairos.db` |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | Required |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth client secret | Required |
| `OPENAI_API_KEY` | OpenAI API key for AI features | Optional |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

### Default Categories

The system initializes with these default categories:
- **Work** (#3B82F6) - Professional events
- **Personal** (#10B981) - Personal activities  
- **Sport** (#F59E0B) - Physical activities
- **Rest** (#8B5CF6) - Rest and relaxation

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues
- **Port 8080 in use**: Change port in `main.py` or kill existing process
- **Database errors**: Run `uv run python migrate.py` to update schema
- **Import errors**: Ensure you're in the correct virtual environment

#### Frontend Issues
- **Port 3000 in use**: Run `npm run dev -- -p 3001` to use different port
- **API connection failed**: Verify backend is running and `NEXT_PUBLIC_API_URL` is correct
- **Build errors**: Clear `.next` folder and `node_modules`, then reinstall

## 📊 Project Status

### Current Version: 0.1.0

### Roadmap

#### Version 0.2.0
- [ ] Recurring events
- [ ] Email notifications
- [ ] Calendar export (iCal)
- [ ] Mobile app (React Native)

#### Version 0.3.0
- [ ] Team collaboration
- [ ] External calendar sync (Google, Outlook)
- [ ] Advanced AI features
- [ ] Analytics dashboard

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent Python web framework
- **Next.js** for the React framework
- **shadcn/ui** for the beautiful UI components
- **SQLAlchemy** for the robust ORM
- **OpenAI** for AI capabilities

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/kairos/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/kairos/discussions)
- **Email**: your-email@example.com

---

<div align="center">

**[🏠 Home](README.md)** • **[📖 Documentation](docs/)** • **[🤝 Contributing](CONTRIBUTING.md)** • **[📋 Changelog](CHANGELOG.md)**

Made with ❤️ by the Kairos team

</div>

