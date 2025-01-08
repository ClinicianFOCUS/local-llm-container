# Ollama Docker Setup

This repository contains a Docker Compose configuration for running Ollama with FastAPI wrapper and Caddy reverse proxy.

## Services

### 1. Ollama

- Base image: `ollama/ollama:latest`
- Provides the core LLM functionality
- GPU support enabled
- Port: 11434

#### Environment Variables

- `NVIDIA_VISIBLE_DEVICES`: Controls GPU visibility (default: all)
- `OLLAMA_CONCURRENT_REQUESTS`: Number of concurrent requests (default: 1)
- `OLLAMA_QUEUE_ENABLED`: Queue system status (default: true)

### 2. FastAPI Wrapper

- Custom-built service using `Dockerfile.wrapper`
- Provides API interface for Ollama
- Port: 5000

#### Environment Variables

- `PYTHONUNBUFFERED`: Set to 1 for unbuffered output
- `SESSION_API_KEY`: Optional API key for session management

### 3. Caddy

- Custom-built service using `Dockerfile.caddy`
- Serves as reverse proxy
- Port: 3334 (configurable)

#### Environment Variables

- `PUBLIC_ACCESS_PORT`: Port configuration (default: 3334)

## Getting Started

1. Clone this repository:

```bash
git clone https://github.com/ClinicianFOCUS/local-llm-container.git
cd local-llm-container
```

2. Launch the services:

```bash
docker-compose up -d
```

## Launching Models

After container deployment, you can launch models using either the CLI or API:

### Using CLI

1. Connect to the Ollama container:

```bash
docker exec -it ollama-service bash
```

2. Pull your desired model:

```bash
ollama pull gemma2:2b-instruct-q8_0
# or any other model
```

3. Run the model:

```bash
ollama run gemma2:2b-instruct-q8_0
```

### Using API

1. Pull a model via API:

```bash
curl -X POST http://localhost:3334/api/pull \
     -H "Content-Type: application/json" \
     -d '{"name": "gemma2:2b-instruct-q8_0"}'
```

2. Generate with the model:

```bash
curl -X POST http://localhost:3334/api/generate \
     -H "Content-Type: application/json" \
     -d '{
           "model": "gemma2:2b-instruct-q8_0",
           "prompt": "Your prompt here"
         }'
```

3. Health Check:

```bash
curl -k https://localhost:3334/health
```

### Available Models

You can find available models at:

- [Ollama Model Library](https://ollama.ai/library)

## Environment Variables

| Variable                   | Default | Description                     |
| -------------------------- | ------- | ------------------------------- |
| NVIDIA_VISIBLE_DEVICES     | all     | GPU devices available to Ollama |
| OLLAMA_CONCURRENT_REQUESTS | 1       | Maximum concurrent requests     |
| OLLAMA_QUEUE_ENABLED       | true    | Enable/disable request queue    |
| SESSION_API_KEY            | -       | API key for FastAPI wrapper     |
| PUBLIC_ACCESS_PORT         | 3334    | External port for Caddy         |

You can set these variables using the CLI:

Windows:

```bash
$env:SESSION_API_KEY="MY_API_KEY_TO_USE__FOR_AUTHENTICATION"
```

Linux:

```bash
export SESSION_API_KEY MY_API_KEY_TO_USE__FOR_AUTHENTICATION
```

# Access the Services

Access the LLM API through the Caddy reverse proxy:

- API Endpoint: `https://localhost:3334/api/`
- Docs: `https://github.com/ollama/ollama/blob/main/docs/api.md`

## License

This project is licensed under the AGPL-3.0 License - see the LICENSE file for details.
