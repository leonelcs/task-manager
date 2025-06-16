#!/bin/bash

# MySQL Connection Script for ADHD Coach Task Manager
# This script connects to the MySQL Docker container with interactive session

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Container and database details
CONTAINER_NAME="adhdcoach-mysql"
DATABASE_NAME="adhd_tasks_dev"
USERNAME="adhd_tasksmanager"
PASSWORD="My:S3cr3t"
ROOT_PASSWORD="rootpassword"

echo -e "${GREEN}ADHD Coach MySQL Connection Script${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if container exists and is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${YELLOW}Container '$CONTAINER_NAME' is not running.${NC}"
    echo "Checking if container exists but is stopped..."
    
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        echo -e "${YELLOW}Starting container '$CONTAINER_NAME'...${NC}"
        docker start "$CONTAINER_NAME"
        echo "Waiting for MySQL to be ready..."
        sleep 10
    else
        echo -e "${RED}Container '$CONTAINER_NAME' does not exist.${NC}"
        echo "Please run 'docker-compose up -d mysql' first."
        exit 1
    fi
fi

# Wait for MySQL to be ready
echo "Checking MySQL connectivity..."
until docker exec "$CONTAINER_NAME" mysqladmin ping -h"localhost" -u"root" -p"$ROOT_PASSWORD" --silent; do
    echo -e "${YELLOW}Waiting for MySQL to be ready...${NC}"
    sleep 2
done

echo -e "${GREEN}MySQL is ready!${NC}"
echo

# Prompt user for connection type
echo "Choose connection type:"
echo "1) Connect as application user ($USERNAME)"
echo "2) Connect as root user"
echo "3) Connect to specific database as application user"
echo "4) Execute custom SQL command"
echo

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}Connecting as application user '$USERNAME'...${NC}"
        docker exec -it "$CONTAINER_NAME" mysql -u "$USERNAME" -p"$PASSWORD"
        ;;
    2)
        echo -e "${GREEN}Connecting as root user...${NC}"
        docker exec -it "$CONTAINER_NAME" mysql -u root -p"$ROOT_PASSWORD"
        ;;
    3)
        echo -e "${GREEN}Connecting to database '$DATABASE_NAME' as '$USERNAME'...${NC}"
        docker exec -it "$CONTAINER_NAME" mysql -u "$USERNAME" -p"$PASSWORD" "$DATABASE_NAME"
        ;;
    4)
        read -p "Enter SQL command: " sql_command
        echo -e "${GREEN}Executing: $sql_command${NC}"
        docker exec -it "$CONTAINER_NAME" mysql -u "$USERNAME" -p"$PASSWORD" "$DATABASE_NAME" -e "$sql_command"
        ;;
    *)
        echo -e "${RED}Invalid choice. Defaulting to application user connection.${NC}"
        docker exec -it "$CONTAINER_NAME" mysql -u "$USERNAME" -p"$PASSWORD"
        ;;
esac

echo -e "${GREEN}Connection closed.${NC}"
