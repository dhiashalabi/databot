# DataBot

A modern AI-powered business data analytics platform that provides natural language interface for querying and analyzing business data. Built with Next.js frontend and FastAPI backend, featuring MCP (Model Context Protocol) integration for intelligent data insights.

## Features

- **Natural Language Queries**: Chat with your data using plain English
- **AI-Powered Analytics**: Leverages OpenAI's GPT models for intelligent data interpretation
- **MCP Integration**: Uses Model Context Protocol for enhanced AI capabilities
- **Modern UI**: Built with Next.js 15, React 19, and Tailwind CSS
- **Real-time Chat Interface**: Interactive chat experience with message history
- **Multi-Model Support**: Choose between different AI models
- **PostgreSQL Database**: Robust data storage with async support
- **Docker Ready**: Containerized for easy deployment

## Coming Soon

- [ ] **File Generation**: Export query results as PDF, Excel, and CSV files for easy sharing and reporting
- [ ] **Charts and Graphs**: Interactive visualizations and data charts to better understand your business metrics
- [ ] **Monitoring**: Real-time system monitoring and performance analytics for optimal data processing
- [ ] **Permissions**: Role-based access control and user management for secure multi-user environments
- [ ] **Token Usage and Restrictions**: Usage tracking, rate limiting, and cost management for OpenAI API calls

## Architecture

```plaintext
databot/
├── frontend/          # Next.js 15 + React 19 + TypeScript
│   ├── app/          # App Router pages
│   ├── components/   # Reusable UI components
│   ├── hooks/        # Custom React hooks
│   └── lib/          # Utilities and configurations
└── backend/          # FastAPI + Python 3.12
    ├── src/
    │   ├── api/      # API endpoints
    │   ├── mcp/      # MCP server implementation
    │   ├── models/   # Database models
    │   └── schemas/  # Pydantic schemas
    └── db/           # Database migrations and setup
```

## Tech Stack

### Frontend

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **UI Components**: Radix UI primitives
- **State Management**: Zustand
- **Data Fetching**: TanStack Query
- **Forms**: React Hook Form + Zod validation
- **Package Manager**: pnpm

### Backend

- **Framework**: FastAPI
- **Language**: Python 3.12
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLAlchemy
- **AI Integration**: OpenAI API + MCP
- **Package Manager**: uv
- **Code Quality**: Ruff + Pre-commit

## Quick Start

### Prerequisites

- Node.js 22+ and pnpm
- Python 3.12+
- PostgreSQL 13+
- OpenAI API key

### 1. Clone the Repository

```bash
git clone https://github.com/dhiashalabi/databot.git
cd databot
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your database and OpenAI credentials

# Start the backend server
fastapi dev main.py
# OR
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Start the development server
pnpm dev
```

The frontend will be available at `http://localhost:3000`.

## Environment Variables

### Backend (.env)

```env
# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=databot

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Application
DEBUG=false
```

### Frontend

The frontend automatically connects to the backend API. No additional environment variables needed for development.

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Individual Services

#### Backend

```bash
cd backend
docker build -t databot-backend .
docker run -p 8000:8000 --env-file .env databot-backend
```

#### Frontend

```bash
cd frontend
docker build -t databot-frontend .
docker run -p 3000:3000 databot-frontend
```

## Usage Examples

Once running, you can interact with your data using natural language:

### Sales Analytics

- "Compare my sales last month and this month"
- "What are my top 5 products by revenue?"
- "Show me sales by category"
- "Total revenue from online vs in-store sales"

### Customer Insights

- "Who are my top 10 customers by spending?"
- "Show me details for customer John Smith"
- "List all corporate customers"

### Product Management

- "Which products are low in stock?"
- "Show me products under $50"

### Financial Data

- "How many pending invoices do I have?"
- "Total value of unpaid invoices"
- "Invoice summary for this month"

## Development

### Code Quality

The project uses several tools to maintain code quality:

- **ESLint + Prettier**: Code formatting and linting
- **Ruff**: Python code formatting and linting
- **Pre-commit**: Git hooks for quality checks
- **TypeScript**: Type safety

### Code Formatting

```bash
# Frontend
cd frontend
pnpm format
pnpm lint:fix

# Backend
cd backend
uv run ruff format .
```

## API Documentation

The backend provides comprehensive API documentation:

- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
