-- MySQL initialization script for ADHD Task Manager
-- This script runs when the MySQL container starts for the first time

-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS adhd_tasks_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create the user if it doesn't exist
CREATE USER IF NOT EXISTS 'adhd_tasksmanager'@'%' IDENTIFIED BY 'My:S3cr3t';

-- Grant privileges
GRANT ALL PRIVILEGES ON adhd_tasks_dev.* TO 'adhd_tasksmanager'@'%';

-- Also grant privileges to localhost connections
CREATE USER IF NOT EXISTS 'adhd_tasksmanager'@'localhost' IDENTIFIED BY 'My:S3cr3t';
GRANT ALL PRIVILEGES ON adhd_tasks_dev.* TO 'adhd_tasksmanager'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Show confirmation
SELECT 'ADHD Task Manager database setup completed!' AS Status;
