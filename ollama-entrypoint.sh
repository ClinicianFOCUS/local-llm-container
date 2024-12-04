#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo "🔴 Pulling gemma2:2b-instruct-q8_0 model..."
ollama pull gemma2:2b-instruct-q8_0
echo "🟢 Successfully pulled gemma2:2b-instruct-q8_0"

echo "🔴 Running gemma2:2b-instruct-q8_0 model..."
ollama run gemma2:2b-instruct-q8_0
echo "🟢 Successfully ran gemma2:2b-instruct-q8_0"

# Wait for Ollama process to finish.
wait $pid