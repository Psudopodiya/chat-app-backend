#!/bin/bash
# Stop and remove all running containers
docker-compose down

# Remove dangling images and unused volumes not associated with any container
docker system prune -a -f --volumes