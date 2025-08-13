# Student Registration Flask Application

## Overview

This project is a student registration system built with Flask and MySQL. It allows users to register students through a web form and view all registered students. The project will be deployed in two phases:

1. **Monolithic Architecture** on an EC2 instance using Ubuntu.
2. **Microservices Architecture**, containerized with Docker and orchestrated using Kubernetes, deployed via CI/CD pipelines.

## Features

- Register students through a web form (`register.html`)
- View all registered students (`student.html`)
- Data stored in a MySQL database
- Built using Flask (Python)
- Initially deployed as a monolithic application
- Later transitioned to microservices (`docker-compose.yml` & `Dockerfile`) and lastly deployed on Kubernetes cluster (`manifest files`), using CI/CD

---

## Monolithic Deployment on EC2

### Step 1: Launch EC2 Instance

- Use **Ubuntu AMI**

### Step 2: System Setup

```bash
sudo apt update
python3 --version   # Check if Python is installed
sudo apt install python3.12-venv -y
```

### Step 3: Project Setup

```bash
mkdir pyapp
cd pyapp
git init
git pull https://github.com/harshkhalkar/student-registration-flask-application.git
```

Use only the following files for now:
- `app.py`
- `requirements.txt`
- `templates/register.html`
- `templates/student.html`
Ignore other files like `Dockerfile`, `docker-compose.yml` and else for now.

### Step 4: MySQL Setup

```bash
sudo apt install mysql-server -y
sudo mysql_secure_installation
```

Login to MySQL:

```bash
sudo mysql
```

Run the following to configure root user and initialize database:

```bash
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_new_password';
FLUSH PRIVILEGES;
EXIT;
```
Then:

```bash
mysql -u root -p < init.sql
```

Or run the SQL manually (see `init.sql` content below).

### Step 5: Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Step 6: Access Application

Visit: http://public-ip:5000

## File Structure (for Monolithic Setup)

```bash
.
├── app.py
├── requirements.txt
├── init.sql
└── templates
    ├── register.html
    └── student.html
```

## Database Schema (`init.sql`)

```sql
CREATE DATABASE IF NOT EXISTS studentsdb;
USE studentsdb;

CREATE TABLE IF NOT EXISTS students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  course VARCHAR(100) NOT NULL,
  address VARCHAR(100) NOT NULL,
  phone VARCHAR(100) NOT NULL,
  contact VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---
# Phase 2: Microservices Architecture (Containerized + CI/CD)

## File Structure 

```bash
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── init.sql
├── requirements.txt
├── templates/
│   ├── register.html
│   └── student.html
├── tests/
│   ├── __init__.py
│   └── test_app.py
```

## Updated requirements.txt

```txt
Flask==2.3.2
mysql-connector-python
Werkzeug<3.0.0
```

## Testing

Create a `tests` directory:

```bash
mkdir tests
touch tests/__init__.py
```

### tests/test_app.py
```
import unittest
from app import app

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_home_status_code(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

# CI/CD Pipeline

```groovy
pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/harshkhalkar/student-registration-flask-application.git'
        BRANCH = '*/main'
        REMOTE_USER = 'ubuntu'
        REMOTE_HOST = '54.224.69.173'
        REMOTE_DIR = '/pyapp'
    }

    stages {

        stage('Clone Repository') {
            steps {
                echo 'Cloning repository...'
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "${BRANCH}"]],
                    userRemoteConfigs: [[url: "${REPO_URL}"]]
                ])
            }
        }

        stage('Install Docker & Compose') {
            steps {
                echo 'Installing Docker & Docker Compose (if not already installed)...'
                sh '''
                    if ! command -v docker &> /dev/null; then
                        sudo apt update -y
                        sudo apt install -y docker.io
                        sudo systemctl start docker
                    fi

                    if ! command -v docker-compose &> /dev/null; then
                        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
                            -o /usr/local/bin/docker-compose
                        sudo chmod +x /usr/local/bin/docker-compose
                    fi

                    docker --version
                    docker-compose --version
                '''
            }
        }

        stage('Build Containers') {
            steps {
                echo 'Starting containers with Docker Compose...'
                sh 'sudo docker-compose up -d --build'
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests inside container...'
                sh '''
                    sudo docker ps
                    curl -s localhost:5000 || echo "Flask app not reachable"
                    sudo docker exec pyapp ls -l
                    sudo docker exec pyapp ls -l tests
                    sudo docker exec pyapp python3 -m unittest discover -s tests -t .
                '''
            }
        }

        stage('Cleanup Local') {
            steps {
                echo 'Cleaning up Docker containers and images...'
                sh '''
                    sudo docker-compose down --volumes --remove-orphans
                    sudo docker image prune -f
                    IMAGES=$(sudo docker images -q)
                    if [ -n "$IMAGES" ]; then
                        sudo docker rmi -f $IMAGES || true
                    else
                        echo "No images to remove"
                    fi
                '''
            }
        }

        stage('Deploy to Remote') {
            steps {
                echo 'Deploying to remote server...'
                script {
                    sshagent(['5db86cd4-3324-4473-bf9b-f2f9f5e397d6']) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
                            set -e
                            echo 'Installing Docker on remote server...'
                            if ! command -v docker &> /dev/null; then
                                sudo apt update -y
                                sudo apt install -y docker.io
                                sudo systemctl start docker
                            fi

                            if ! command -v docker-compose &> /dev/null; then
                                sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\\\$(uname -s)-\\\$(uname -m)" \
                                    -o /usr/local/bin/docker-compose
                                sudo chmod +x /usr/local/bin/docker-compose
                            fi

                            echo 'Preparing deployment directory...'
                            mkdir -p ${REMOTE_DIR}
                            cd ${REMOTE_DIR}

                            if [ ! -d .git ]; then
                                git init
                                git remote add origin ${REPO_URL}
                            fi

                            git fetch origin
                            git reset --hard origin/main

                            echo 'Starting app...'
                            rm -rf kubernetes LICENSE
                            sudo docker-compose up -d --build
                            ENDSSH
                        """
                    }
                }
            }
        }
    }
}

```

## Jenkins Setup Summary
1. Install Jenkins and Access Dashboard
2. Install Plugins:
    - SSH Agent
3. Add Credentials:
    - Type: SSH Username with Private Key
4. Configure Project:
    - Create new item → Pipeline
    - Set GitHub webhook trigger
    - Use inline pipeline script or Jenkinsfile from repo.
Use inline pipeline script or Jenkinsfile from repo
5. Allow Jenkins to use sudo Docker (on both Jenkins & EC2 Live Server):
   
   Run:
   ```bash
   sudo visudo
   ```

   add:
   ```bash
   jenkins ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/docker, /usr/bin/docker-compose
   ```

   or:
   ```bash
   sudo usermod -aG docker jenkins
   ```

---
## Learn More: Jenkins, Docker, Kubernetes

### Jenkins
https://github.com/harshkhalkar/jenkins.git

### Docker
https://github.com/harshkhalkar/Docker.git

### Kubernetes
https://github.com/harshkhalkar/kubernetes.git
