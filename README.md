# Investing API

A Flask-based API for tracking stocks and InfoMoney news using a clean architecture approach.

## Project Overview

This project provides a RESTful API for:
- Fetching and storing stock data from InfoMoney
- Retrieving news articles related to stocks
- Scheduled data collection and updates

The application follows clean architecture principles with:
- Repository layer for database operations
- Domain layer for business logic
- Application layer for orchestration
- Service layer for external data fetching
- RESTful API routes using Flask

## Docker Setup

### Prerequisites

- Docker and Docker Compose installed
- Git (for cloning the repository)

### Development Environment

The development environment includes:
- Flask development server with debugging enabled
- Live code reloading
- Remote debugging capabilities (port 5678)
- PostgreSQL database

To build and run the development environment:

```bash
# Build and start containers
docker-compose build
docker-compose up

# Or in one command
docker-compose up --build
```

### Production Environment

The production environment includes:
- Multi-stage Docker build for smaller image size
- Gunicorn WSGI server with proper worker configuration
- Non-root user for improved security
- Health checks for container orchestration
- Scheduled tasks for data collection
- PostgreSQL database

#### Direct Docker Build Commands

If you need to build the images directly without using docker-compose:

```bash
# Build the Flask application image
docker build -t flask_app_prod -f Dockerfile.prod .

# Pull the PostgreSQL image
docker pull postgres:14
```

#### Building for Multiple Architectures

If you need to run your Docker image on different architectures (e.g., ARM64 vs AMD64), you should build multi-architecture images:

```bash
# Enable Docker BuildKit
export DOCKER_BUILDKIT=1

# Set up Docker Buildx (if not already set up)
docker buildx create --name mybuilder --use

# Build and push multi-architecture image directly to Docker Hub
docker buildx build --platform linux/amd64,linux/arm64 \
  -t lucaslotti/invest-app:1.0.0 \
  -f Dockerfile.prod \
  --push .
```

Alternatively, you can specify the target platform when building:

```bash
# Build for a specific platform
docker build --platform linux/arm64 -t flask_app_prod -f Dockerfile.prod .
```

#### Tagging and Pushing to Docker Hub

To push your images to Docker Hub:

```bash
# Login to Docker Hub
docker login

# Tag your Flask application image
docker tag flask_app_prod lucaslotti/invest-app:1.0.0

# Push the tagged image to Docker Hub
docker push lucaslotti/invest-app:1.0.0
```

To pull the image on another machine:

```bash
# Pull the image (Docker will automatically select the right architecture)
docker pull lucaslotti/invest-app:1.0.0
```

To run the containers after building:

```bash
# Create a custom network for the containers
docker network create investing_network

# Run PostgreSQL container
docker run -d --name postgres_db_prod \
  --network investing_network \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=investing \
  -p 5432:5432 \
  postgres:14

# Run Flask application container
docker run -d --name flask_app_prod \
  --network investing_network \
  -e PYTHONUNBUFFERED=1 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=investing \
  -e POSTGRES_HOST=postgres_db_prod \
  -e POSTGRES_PORT=5432 \
  -e SECRET_KEY=production-secret-key-change-me \
  -e FLASK_ENV=production \
  -e FLASK_APP=app.py \
  -e SCHEDULER_ENABLED=true \
  -e API_BASE_URL=http://localhost:5000 \
  -p 5000:5000 \
  flask_app_prod
```

#### Using Docker Compose

Alternatively, you can use docker-compose to build and run both containers:

```bash
# Build and start containers
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up

# Or in one command
docker-compose -f docker-compose.prod.yml up --build
```

### Running in WSL (Windows Subsystem for Linux)

If you're using WSL, you can run the commands from the WSL terminal:

```bash
# Development
cd /mnt/c/Users/boave/investing/invest/project
docker-compose up --build

# Production
cd /mnt/c/Users/boave/investing/invest/project
docker-compose -f docker-compose.prod.yml up --build
```

## Scheduled Tasks

The production environment includes a scheduler that automatically runs the following tasks:

| Task | Endpoint | Schedule | Description |
|------|----------|----------|-------------|
| Fetch Stocks | GET /api/stocks/fetch | Daily at 1:00 AM | Fetches stock data from external sources |
| Save Stock URLs | GET /api/news/save-stock-urls | Daily at 2:00 AM | Saves news URLs for stocks |
| Fetch News | POST /api/news/fetch | Daily at 3:00 AM | Fetches news from InfoMoney |
| Update News Content | POST /api/news/update-content | Daily at 4:00 AM | Updates news content |

The scheduler is enabled by default in the production environment.

## API Documentation

API documentation is available at `/apidocs/` when the application is running. This provides an interactive Swagger UI for exploring and testing the API endpoints.

## Environment Variables

### Common Variables

- `POSTGRES_USER`: PostgreSQL username (default: postgres)
- `POSTGRES_PASSWORD`: PostgreSQL password (default: postgres)
- `POSTGRES_DB`: PostgreSQL database name (default: investing)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `SECRET_KEY`: Flask secret key

### Development-Specific Variables

- `FLASK_ENV`: Set to "development"
- `FLASK_DEBUG`: Set to 1
- `POSTGRES_HOST`: Set to "localhost" (when using host networking)

### Production-Specific Variables

- `FLASK_ENV`: Set to "production"
- `SCHEDULER_ENABLED`: Set to "true" to enable scheduled tasks
- `API_BASE_URL`: Base URL for API requests (default: http://app:5000)
- `POSTGRES_HOST`: Set to "db" (container name)

## Database Migrations

Database migrations are handled automatically when the containers start up. If you need to run migrations manually:

```bash
# Development
docker-compose exec app flask db upgrade

# Production
docker-compose -f docker-compose.prod.yml exec app flask db upgrade
```

## Project Structure

```
project/
├── app.py                  # Main Flask application
├── Dockerfile              # Development Dockerfile
├── Dockerfile.prod         # Production Dockerfile
├── docker-compose.yml      # Development Docker Compose
├── docker-compose.prod.yml # Production Docker Compose
├── requirements.txt        # Python dependencies
├── lib/                    # Application code
│   ├── application/        # Application layer
│   ├── db/                 # Database models and repositories
│   ├── domain/             # Domain layer
│   ├── migrations/         # Database migrations
│   ├── services/           # External services
│   └── utils/              # Utilities
└── routes/                 # API routes
```
