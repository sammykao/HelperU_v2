# Docker Setup for HelperU Backend

This guide explains how to run the HelperU backend using Docker with all the AI agent functionality.

## Prerequisites

1. **Docker** installed on your system
2. **Docker Compose** installed
3. **Environment variables** configured

## Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
cp env.template .env
```

Edit the `.env` file with your actual values:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
STRIPE_PREMIUM_PRICE_ID=your_stripe_premium_price_id

# OpenPhone Configuration
OPENPHONE_API_KEY=your_api_key
OPENPHONE_FROM_NUMBER=open_phone_number(starts with +)

# AI Configuration
OPENAI_API_KEY=your_openai_api_key
```

### 2. Build and Run with Docker Compose

```bash
# Build and start the container
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### 3. Run with Docker directly

```bash
# Build the image
docker build -t helperu-backend .

# Run with environment variables
docker run -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  helperu-backend

# Run with specific environment variables
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_ANON_KEY=your_key \
  helperu-backend
```

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI agents | `sk-...` |
| `SUPABASE_URL` | Supabase project URL | `https://...` |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | `eyJ...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment mode | `production` |
| `STRIPE_SECRET_KEY` | Stripe secret key | - |
| `OPENPHONE_API_KEY` | OpenPhone API key | - |

## Dependencies

The Docker image includes all necessary dependencies:

- **LangChain**: `>=0.3.27` - AI framework
- **LangGraph**: `>=0.6.6` - Stateful AI systems
- **LangGraph Supervisor**: `>=0.0.1` - Multi-agent orchestration
- **LangGraph Checkpoint SQLite**: `>=0.0.1` - Persistent memory
- **LangChain OpenAI**: `>=0.1.0` - OpenAI integration
- **OpenAI**: `>=1.0.0` - OpenAI API client
- **ChromaDB**: `>=0.4.0` - Vector database
- **Tiktoken**: `>=0.5.0` - Token counting
- **Requests**: `>=2.31.0` - HTTP library

## Health Check

The container includes a health check that verifies the API is running:

```bash
# Check health status
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Data Persistence

The AI agent memory and data are persisted in the `./data` directory:

```bash
# Create data directory
mkdir -p data

# The container will mount this directory
-v $(pwd)/data:/app/data
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Use a different port
   docker run -p 8001:8000 helperu-backend
   ```

2. **Environment variables not loaded**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Verify environment variables
   docker-compose config
   ```

3. **Build fails**
   ```bash
   # Clean build
   docker-compose build --no-cache
   
   # Check Docker logs
   docker-compose logs
   ```

4. **AI agent errors**
   ```bash
   # Check OpenAI API key
   echo $OPENAI_API_KEY
   
   # Test OpenAI connection
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

### Logs and Debugging

```bash
# View container logs
docker-compose logs -f helperu-backend

# Access container shell
docker-compose exec helperu-backend /bin/bash

# Check environment variables in container
docker-compose exec helperu-backend env | grep -E "(OPENAI|SUPABASE|STRIPE)"
```

## Development

### Local Development

For local development without Docker:

```bash
# Install dependencies
uv sync

# Run locally
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

Run the AI agent tests:

```bash
# Run simple test
cd tests
python test_ai_agent_simple.py

# Run comprehensive test
python test_ai_agent_client.py
```

## Production Deployment

### Docker Compose Production

```bash
# Production compose file
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: helperu-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: helperu-backend
  template:
    metadata:
      labels:
        app: helperu-backend
    spec:
      containers:
      - name: helperu-backend
        image: helperu-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: helperu-secrets
              key: openai-api-key
```

## Monitoring

### Health Checks

```bash
# Automated health check
curl -f http://localhost:8000/health

# Manual health check
curl http://localhost:8000/health
```

### Metrics

The application exposes metrics at `/metrics` (if configured):

```bash
curl http://localhost:8000/metrics
```

## Security

### Environment Variables

- Never commit `.env` files to version control
- Use Docker secrets for production
- Rotate API keys regularly

### Network

- Use internal networks for service communication
- Expose only necessary ports
- Use reverse proxy for SSL termination

## Support

For issues and questions:

1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Test individual components
4. Check the main README.md for more details
