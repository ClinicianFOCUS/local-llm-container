#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

# Pull the model with error handling
echo "🔴 Pulling gemma2:2b-instruct-q8_0 model..."
if ollama pull gemma2:2b-instruct-q8_0; then
    echo "🟢 Successfully pulled gemma2:2b-instruct-q8_0"
else
    echo "🔴 Failed to pull gemma2:2b-instruct-q8_0"
    exit 1
fi

# Run the model with error handling
echo "🔴 Running gemma2:2b-instruct-q8_0 model..."
if ollama run gemma2:2b-instruct-q8_0; then
    echo "🟢 Successfully ran gemma2:2b-instruct-q8_0"
else
    echo "🔴 Failed to run gemma2:2b-instruct-q8_0"
    exit 1
fi

# Wait for Ollama process to finish.
wait $pid