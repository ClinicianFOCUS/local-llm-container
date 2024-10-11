## Summary

Repository for the setup of a local LLM container to support other activities and tools we are developing. This setup allows you to run a local instance of a Language Model (LLM) with GPU support and access it via HTTPS using Caddy reverse proxy.

# Prerequisites

- Docker and Docker Compose installed on your system.
- NVIDIA Docker runtime for GPU support. Installation guide [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

# Setup

1. Clone the Repository:

   ```bash
   git clone https://github.com/ClinicianFOCUS/local-llm-container.git
   cd local-llm-container
   ```

2. Download the LLM model you want to use and place it in the `/models` folder.

# Environment Variables

The following environment variables can be set to configure the services:

- `MODEL_NAME`: The path to the LLM model file. Default is `/models/gemma-2-2b-it`.
- `LLM_CONTAINER_PORT`: The port on which the LLM container will be accessible. Default is `3334`.

You can set these variables using the CLI:

Windows:

```bash
$env:MODEL_NAME='/models/you_models_folder'
```

Linux:

```bash
export MODEL_NAME /models/you_models_folder
```

# Start the Services

Use Docker Compose to start the services:

```bash
docker-compose up -d
```

# Access the Services

Access the LLM API through the Caddy reverse proxy:

- OpenAI API: `https://localhost:3334/v1/`
- Docs: `https://localhost:3334/docs/`
- OpenAI API Docs: `https://platform.openai.com/docs/api-reference/introduction`
