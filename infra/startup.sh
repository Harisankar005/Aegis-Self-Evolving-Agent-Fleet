#!/bin/bash

echo "📦 Starting Aegis Agent Fleet Infrastructure..."
docker-compose -f docker-compose.yml up --build
chmod +x infra/startup.sh
