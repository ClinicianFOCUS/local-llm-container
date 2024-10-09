.. Local-LLM-Container documentation master file, created by
   sphinx-quickstart on Wed Oct  9 09:26:35 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================
Unburdening Primary Healthcare
==============================

Welcome to the **Unburdening Primary Healthcare: An Open-Source AI Clinician Partner Platform** documentation. This project is a collaboration as part of the ClinicianFOCUS initiative with Conestoga College and Dr. Braedon Hendy. Below you'll find documentation for the core modules, API endpoints, and utilities used in this project. Below are the pages contents:

.. contents::
   :depth: 2
   :local:


Docker-Compose Setup
====================

This documentation provides an overview of the Docker Compose configuration for the project, including the `llm-container` and `caddy` services.

Prerequisites
-------------

- **Docker** and **Docker Compose** must be installed on your system. (https://docs.docker.com/engine/install/)
- **Nvidia Docker runtime** must be installed. (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- **Nvidia CUDA Toolkit** must be installed. (https://developer.nvidia.com/cuda-downloads)


Installation
------------

Follow these steps to set up and run the services using Docker Compose:

1. **Clone the repository**:

   .. code-block:: bash

      git clone https://github.com/ClinicianFOCUS/local-llm-container.git
      cd local-llm-container

2. **Ensure Docker and Docker Compose are installed**. You can install Docker by following the instructions on the [official Docker website](https://docs.docker.com/get-docker/).

3. **Load your model**:

   The LLM model is not included in the repository. You can download the model from the Huggingface (https://huggingface.co/)

   We recommend installing Gemma-2-2b-it (https://huggingface.co/google/gemma-2-2b-it).

   After downloading the model, place it in the `llm-container/models` directory and update the `MODEL_NAME` environment variable to the folder name of your model;

   **Windows**

      .. code-block:: bash

            $env:MODEL_NAME="/models/gemma-2-2b-it"

   **Linux**

      .. code-block:: bash

            MODEL_NAME=/models/gemma-2-2b-it


4. **Build and start the services**:

   .. code-block:: bash

      docker-compose up -d --build

   This command will build the Docker images defined in the `Dockerfile.llm-cont` and `Dockerfile.caddy`, and start both the `llm-container` and `caddy` services.

5. **Verify the services are running**:

   After the services start, you can check that the LLM model and Caddy web server are running correctly by accessing:

   - **LLM Service**: Runs internally in the Docker container.
   - **Caddy Web Server**: Accessible on port 3334 at `https://localhost:3334`. Pointing to the LLM Serivce.

Usage
-----

**Running the Containers**

To start the containers and ensure everything is running correctly, use the following command:

.. code-block:: bash

   docker-compose up -d

This command will:
- Launch the `llm-container` for running the language model.
- Start the `caddy` container to serve content via the Caddy web server.

You can access the services on `https://localhost:3334/docs` to interact with the Caddy server and the deployed LLM model.

**Stopping the Containers**

To stop the containers:

.. code-block:: bash

   docker-compose down

This will stop and remove the containers, but the built images and mounted volumes will persist.


Additonal Notes
===============

This service runs on the aphrodite engine. For additional help or support, please check out their github and documentation https://github.com/PygmalionAI/aphrodite-engine.