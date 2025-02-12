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

# create the model from the model file
if ollama create gemma2-2b-q8-8k-context -f ./Modelfile; then
    echo "🟢 Successfully created gemma2-2b-q8-8k-context"
else
    echo "🔴 Failed to create gemma2-2b-q8-8k-context"
    exit 1
fi

# run the new model
if ollama run gemma2-2b-q8-8k-context; then
    echo "🟢 Successfully ran gemma2-2b-q8-8k-context"
else
    echo "🔴 Failed to run gemma2-2b-q8-8k-context"
    exit 1
fi

# Wait for Ollama process to finish.
wait $pid