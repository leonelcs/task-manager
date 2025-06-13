# GCP Cloud SQL Setup Instructions

## Prerequisites
1. GCP Project with Cloud SQL Admin API enabled
2. Cloud SQL MySQL instance created
3. Service account with Cloud SQL Client role

## Cloud SQL Instance Setup

### 1. Create Cloud SQL Instance
```bash
gcloud sql instances create adhd-task-manager \
    --database-version=MYSQL_8_0 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=YOUR_SECURE_PASSWORD \
    --authorized-networks=0.0.0.0/0
```

### 2. Create Database
```bash
gcloud sql databases create adhd_tasks_prod \
    --instance=adhd-task-manager
```

### 3. Create User
```bash
gcloud sql users create adhd_user \
    --instance=adhd-task-manager \
    --password=YOUR_USER_PASSWORD
```

## Environment Configuration

### For App Engine/Cloud Run (Unix Socket)
```env
ENVIRONMENT=production
CLOUD_SQL_CONNECTION_NAME=your-project:us-central1:adhd-task-manager
DB_NAME=adhd_tasks_prod
DB_USER=adhd_user
DB_PASSWORD=your-user-password
```

### For Compute Engine (TCP Connection)
```env
ENVIRONMENT=production
DB_HOST=CLOUD_SQL_PRIVATE_IP
DB_PORT=3306
DB_NAME=adhd_tasks_prod
DB_USER=adhd_user
DB_PASSWORD=your-user-password
```

## Deployment Commands

### 1. Run Migrations
```bash
# Set environment
export ENVIRONMENT=production

# Run migrations
alembic upgrade head
```

### 2. Deploy to App Engine
Create `app.yaml`:
```yaml
runtime: python311

env_variables:
  ENVIRONMENT: production
  CLOUD_SQL_CONNECTION_NAME: your-project:us-central1:adhd-task-manager
  DB_NAME: adhd_tasks_prod
  DB_USER: adhd_user
  DB_PASSWORD: your-user-password
  SECRET_KEY: your-production-secret-key

beta_settings:
  cloud_sql_instances: your-project:us-central1:adhd-task-manager
```

### 3. Deploy to Cloud Run
```bash
gcloud run deploy adhd-task-manager \
    --source . \
    --platform managed \
    --region us-central1 \
    --set-env-vars ENVIRONMENT=production \
    --set-env-vars CLOUD_SQL_CONNECTION_NAME=your-project:us-central1:adhd-task-manager \
    --set-env-vars DB_NAME=adhd_tasks_prod \
    --set-env-vars DB_USER=adhd_user \
    --set-env-vars DB_PASSWORD=your-user-password \
    --set-env-vars SECRET_KEY=your-production-secret-key \
    --add-cloudsql-instances your-project:us-central1:adhd-task-manager
```

## Local MySQL Testing

### 1. Install MySQL locally
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# macOS
brew install mysql
```

### 2. Create local database
```sql
CREATE DATABASE adhd_tasks_dev;
CREATE USER 'adhd_user'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON adhd_tasks_dev.* TO 'adhd_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Update .env.local
```env
DATABASE_URL=mysql+pymysql://adhd_user:dev_password@localhost:3306/adhd_tasks_dev
```
