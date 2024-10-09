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

Installation
------------

Follow these steps to set up and run the services using Docker Compose:

1. **Clone the repository**:

   .. code-block:: bash

      git clone https://github.com/ClinicianFOCUS/local-llm-container.git
      cd local-llm-container

2. **Ensure Docker and Docker Compose are installed**. You can install Docker by following the instructions on the [official Docker website](https://docs.docker.com/get-docker/).

3. **Build and start the services**:

   .. code-block:: bash

      docker-compose up -d --build

   This command will build the Docker images defined in the `Dockerfile.llm-cont` and `Dockerfile.caddy`, and start both the `llm-container` and `caddy` services.

4. **Verify the services are running**:

   After the services start, you can check that the LLM model and Caddy web server are running correctly by accessing:

   - **LLM Service**: Runs internally in the Docker container.
   - **Caddy Web Server**: Accessible on port 3334 at `https://localhost:3334`. Pointing to the LLM Serivce.

Usage
-----

Running the Containers

To start the containers and ensure everything is running correctly, use the following command:

.. code-block:: bash

   docker-compose up -d

This command will:
- Launch the `llm-container` for running the language model.
- Start the `caddy` container to serve content via the Caddy web server.

You can access the services on `https://localhost:3334/docs` to interact with the Caddy server and the deployed LLM model.

### Stopping the Containers

To stop the containers:

.. code-block:: bash

   docker-compose down

This will stop and remove the containers, but the built images and mounted volumes will persist.


Additonal Notes
===============

This service runs on the aphrodite engine. For additional help or support, please check out their github and documentation https://github.com/PygmalionAI/aphrodite-engine.