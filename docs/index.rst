Ollama Docker Setup
==================

Welcome to the Ollama Docker Setup documentation! This guide will help you set up and run Ollama with FastAPI wrapper and Caddy reverse proxy using Docker Compose.

Services Overview
---------------

The setup consists of three main services:

Ollama Service
^^^^^^^^^^^^^

The core service providing LLM functionality:

* Based on ``ollama/ollama:latest`` image
* GPU support enabled
* Runs on port 11434
* Configurable through environment variables:

  * ``NVIDIA_VISIBLE_DEVICES``: Controls GPU visibility (default: all)
  * ``OLLAMA_CONCURRENT_REQUESTS``: Number of concurrent requests (default: 1)
  * ``OLLAMA_QUEUE_ENABLED``: Queue system status (default: true)

FastAPI Wrapper
^^^^^^^^^^^^^

A custom service providing API interface:

* Built using custom ``Dockerfile.wrapper``
* Runs on port 5000
* Environment variables:

  * ``PYTHONUNBUFFERED``: Set to 1 for unbuffered output
  * ``SESSION_API_KEY``: Optional API key for session management

Caddy Service
^^^^^^^^^^^^

Reverse proxy service:

* Built using custom ``Dockerfile.caddy``
* Runs on port 3334 (configurable)
* Environment variables:

  * ``PUBLIC_ACCESS_PORT``: Port configuration (default: 3334)

Installation
-----------

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/ClinicianFOCUS/local-llm-container.git
   cd local-llm-container

2. Launch the services:

.. code-block:: bash

   docker-compose up -d

Using the Services
----------------

Launching Models
^^^^^^^^^^^^^^

You can launch models using either the CLI or API interface.

CLI Method
~~~~~~~~~

1. Connect to the Ollama container:

.. code-block:: bash

   docker exec -it ollama-service bash

2. Pull your desired model:

.. code-block:: bash

   ollama pull gemma2:2b-instruct-q8_0

3. Run the model:

.. code-block:: bash

   ollama run gemma2:2b-instruct-q8_0

API Method
~~~~~~~~~

1. Pull a model via API:

.. code-block:: bash

   curl -X POST http://localhost:3334/api/pull \
        -H "Content-Type: application/json" \
        -d '{"name": "gemma2:2b-instruct-q8_0"}'

2. Generate with the model:

.. code-block:: bash

   curl -X POST http://localhost:3334/api/generate \
        -H "Content-Type: application/json" \
        -d '{
              "model": "gemma2:2b-instruct-q8_0",
              "prompt": "Your prompt here"
            }'

Configuration
------------

Environment Variables
^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Variable
     - Default
     - Description
   * - NVIDIA_VISIBLE_DEVICES
     - all
     - GPU devices available to Ollama
   * - OLLAMA_CONCURRENT_REQUESTS
     - 1
     - Maximum concurrent requests
   * - OLLAMA_QUEUE_ENABLED
     - true
     - Enable/disable request queue
   * - SESSION_API_KEY
     - -
     - API key for FastAPI wrapper
   * - PUBLIC_ACCESS_PORT
     - 3334
     - External port for Caddy

Setting Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^

Windows:

.. code-block:: powershell

   $env:MODEL_NAME='/models/you_models_folder'

Linux:

.. code-block:: bash

   export MODEL_NAME /models/you_models_folder

Accessing the Services
-------------------

Access the LLM API through the Caddy reverse proxy:

* API Endpoint: ``https://localhost:3334/api/``
* API Documentation: `Ollama API Docs <https://github.com/ollama/ollama/blob/main/docs/api.md>`_

Resources
--------

* Available models can be found at the `Ollama Model Library <https://ollama.ai/library>`_

License
-------

This project is licensed under the AGPL-3.0 License - see the LICENSE file for details.